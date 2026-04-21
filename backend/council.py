import asyncio
import json
from dataclasses import dataclass, field
from typing import AsyncGenerator

from backend.agents.appraiser import Appraiser
from backend.agents.critic import Critic
from backend.agents.judge import Judge
from backend.models import CouncilResult, DebateMessage, ScoreCard, Verdict


@dataclass
class CouncilEvent:
    type: str  # "chunk" | "message" | "score" | "refined" | "done"
    agent: str | None = None
    content: str | None = None
    round: int = 0
    score_card: ScoreCard | None = None
    refined_idea: str | None = None
    summary: str | None = None


class Council:
    def __init__(self):
        self.critic = Critic()
        self.appraiser = Appraiser()
        self.judge = Judge()

    async def run(
        self,
        idea: str,
        iterations: int = 1,
        turns_per_round: int = 3,
        description: str = "",
    ) -> AsyncGenerator[CouncilEvent, None]:
        refined = idea

        for iteration in range(1, iterations + 1):
            yield CouncilEvent(type="message", agent=None, content=f"Iteration {iteration}", round=iteration)

            full_idea = f"{refined}\n\n{description}" if description else refined
            history: list[DebateMessage] = []
            current_idea = refined

            for turn in range(1, turns_per_round + 1):
                critic_out = ""
                async for chunk in self.critic.stream_respond(full_idea, history):
                    critic_out += chunk
                    yield CouncilEvent(type="chunk", agent=self.critic.name, content=chunk, round=iteration)
                history.append(
                    DebateMessage(
                        agent=self.critic.name,
                        role="critic",
                        content=critic_out,
                        round=iteration,
                    )
                )
                yield CouncilEvent(type="message", agent=self.critic.name, content=critic_out, round=iteration)

                appraiser_out = ""
                async for chunk in self.appraiser.stream_respond(full_idea, history):
                    appraiser_out += chunk
                    yield CouncilEvent(type="chunk", agent=self.appraiser.name, content=chunk, round=iteration)
                history.append(
                    DebateMessage(
                        agent=self.appraiser.name,
                        role="appraiser",
                        content=appraiser_out,
                        round=iteration,
                    )
                )
                yield CouncilEvent(type="message", agent=self.appraiser.name, content=appraiser_out, round=iteration)

            judge_out = await self.judge.respond(full_idea, history)

            verdict = self._parse_verdict(judge_out)

            yield CouncilEvent(
                type="score",
                agent=self.judge.name,
                score_card=verdict.score_card,
                round=iteration,
            )
            yield CouncilEvent(
                type="refined",
                agent=self.judge.name,
                content=verdict.refined_idea,
                round=iteration,
            )

            refined = verdict.refined_idea

        yield CouncilEvent(type="done", agent=None, content=refined, round=iterations)

    def _parse_verdict(self, raw: str) -> Verdict:
        json_start = -1
        for i, char in enumerate(raw):
            if char == "{":
                potential = raw[i:]
                if '"score_card"' in potential or '"viability"' in potential:
                    json_start = i
                    break

        if json_start == -1:
            raise ValueError(f"Could not find JSON in output: {raw[:200]}")

        json_str = raw[json_start:]
        brace_count = 0
        json_end = len(json_str)
        for i, char in enumerate(json_str):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        data = json.loads(json_str[:json_end])
        return Verdict(
            score_card=ScoreCard(**data["score_card"]),
            refined_idea=data["refined_idea"],
            summary=data["summary"],
        )


async def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("idea", nargs="?", default="A subscription box for hackers")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--turns", type=int, default=3)
    args = parser.parse_args()

    council = Council()
    print(f"Idea: {args.idea}")
    print(f"Iterations: {args.iterations} | Turns per round: {args.turns}")
    print("-" * 40)
    async for event in council.run(args.idea, args.iterations, args.turns):
        if event.type == "chunk":
            print(event.content, end="", flush=True)
        elif event.type == "message":
            pass  # already printed via chunks
        elif event.type == "score" and event.score_card:
            print(f"\n\n=== SCORES (Round {event.round}) ===")
            for dim in ["viability", "novelty", "risk", "potential"]:
                score = getattr(event.score_card, dim)
                print(f"  {dim}: {score.score}/10 — {score.reasoning}")
        elif event.type == "refined":
            print(f"\n=== REFINED (Round {event.round}) ===")
            print(event.content)
        elif event.type == "done":
            print(f"\n\n=== FINAL IDEA ===")
            print(event.content)


if __name__ == "__main__":
    asyncio.run(main())