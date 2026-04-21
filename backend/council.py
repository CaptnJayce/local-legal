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
    type: str
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
                critic_out = await self.critic.respond(full_idea, history)
                history.append(
                    DebateMessage(
                        agent=self.critic.name,
                        role="critic",
                        content=critic_out,
                        round=iteration,
                    )
                )
                yield CouncilEvent(type="message", agent=self.critic.name, content=critic_out, round=iteration)

                appraiser_out = await self.appraiser.respond(full_idea, history)
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
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"Could not parse verdict from output: {raw[:200]}")
        json_str = raw[start:end]
        data = json.loads(json_str)
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
    async for event in council.run(args.idea, args.iterations, args.turns):
        if event.type == "message":
            print(f"\n=== {event.agent} (Round {event.round}) ===")
            print(event.content)
        elif event.type == "score" and event.score_card:
            print(f"\n=== SCORES (Round {event.round}) ===")
            for dim in ["viability", "novelty", "risk", "potential"]:
                score = getattr(event.score_card, dim)
                print(f"  {dim}: {score.score}/10 — {score.reasoning}")
        elif event.type == "refined":
            print(f"\n=== REFINED (Round {event.round}) ===")
            print(event.content)
        elif event.type == "done":
            print(f"\n=== DONE ===")
            print(f"Final idea: {event.content}")


if __name__ == "__main__":
    asyncio.run(main())