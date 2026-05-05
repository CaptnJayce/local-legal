import asyncio
import json
import re
from typing import AsyncGenerator, Literal

from pydantic import BaseModel

from backend.agents.appraiser import Appraiser
from backend.agents.critic import Critic
from backend.agents.judge import Judge
from backend.models import CouncilResult, DebateMessage, ScoreCard, Verdict


class CouncilEvent(BaseModel):
    type: Literal["chunk", "message", "score", "refined", "done"]
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
        *,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> AsyncGenerator[CouncilEvent, None]:
        refined = idea
        llm_kwargs = {"provider": provider, "model": model, "api_key": api_key}

        for iteration in range(1, iterations + 1):
            yield CouncilEvent(type="message", agent=None, content=f"Iteration {iteration}", round=iteration)

            full_idea = f"{refined}\n\n{description}" if description else refined
            history: list[DebateMessage] = []

            for turn in range(1, turns_per_round + 1):
                critic_out = ""
                async for chunk in self.critic.stream_respond(full_idea, history, **llm_kwargs):
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
                async for chunk in self.appraiser.stream_respond(full_idea, history, **llm_kwargs):
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

            yield CouncilEvent(type="message", agent=self.judge.name, content="Scoring...", round=iteration)

            judge_out = await self.judge.respond(full_idea, history, **llm_kwargs)

            verdict = self._parse_verdict(judge_out, fallback_idea=refined)

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

    def _parse_verdict(self, raw: str, fallback_idea: str = "") -> Verdict:
        cleaned = raw.strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if not match:
                raise ValueError(f"Could not find JSON in Judge output: {raw[:200]}")
            data = json.loads(match.group())

        score_card = data.setdefault("score_card", {})
        for dim in ("viability", "novelty", "risk", "potential"):
            score_card.setdefault(dim, {"score": 5, "reasoning": "Not assessed."})

        if isinstance(data.get("refined_idea"), dict):
            data["refined_idea"] = " ".join(str(v) for v in data["refined_idea"].values())
        if not data.get("refined_idea"):
            data["refined_idea"] = fallback_idea

        if isinstance(data.get("summary"), dict):
            data["summary"] = " ".join(str(v) for v in data["summary"].values())
        if not data.get("summary"):
            data["summary"] = "No summary provided."

        return Verdict.model_validate(data)


def _colour(text: str, colour: str) -> str:
    codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    return f"{codes.get(colour, '')}{text}{codes['reset']}"


async def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("idea", nargs="?", default="A subscription box for hackers")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--turns", type=int, default=3)
    parser.add_argument("--no-color", action="store_true", help="Disable coloured output")
    args = parser.parse_args()

    use_colour = not args.no_color and sys.stdout.isatty()

    def c(text: str, colour: str) -> str:
        return text if not use_colour else _colour(text, colour)

    council = Council()

    print()
    print(c("═" * 50, "cyan"))
    print(c("  LOCAL LEGAL COUNCIL", "bold"))
    print(c("═" * 50, "cyan"))
    print()
    print(c(f"  Idea: ", "bold") + args.idea)
    print(c(f"  Iterations: {args.iterations}  |  Turns: {args.turns}", "yellow"))
    print()
    print(c("─" * 50, "cyan"))
    print()

    current_agent = None

    async for event in council.run(args.idea, args.iterations, args.turns):
        if event.type == "chunk":
            if event.agent != current_agent:
                if current_agent is not None:
                    print()
                    print(c("─" * 50, "cyan"))
                    print()
                colour = {"Critic": "red", "Appraiser": "green", "Judge": "yellow"}.get(event.agent, "white")
                print(c(f"┌─ {event.agent.upper()} ", colour) + c("─" * 30, "cyan"))
                current_agent = event.agent
            print(event.content, end="", flush=True)

        elif event.type == "score" and event.score_card:
            current_agent = None
            print()
            print(c("─" * 50, "cyan"))
            print()
            print(c(f"  ⚖ JUDGE'S SCORECARD — Round {event.round}", "bold yellow"))
            print()
            for dim in ["viability", "novelty", "risk", "potential"]:
                score = getattr(event.score_card, dim)
                bar = "█" * score.score + "░" * (10 - score.score)
                print(f"    {dim:10} {bar} {score.score}/10")
                print(f"              {score.reasoning}")
                print()

        elif event.type == "refined":
            print()
            print(c("─" * 50, "cyan"))
            print()
            print(c(f"  ✨ REFINED IDEA — Round {event.round}", "bold cyan"))
            print()
            print(f"  {event.content}")
            print()

        elif event.type == "done":
            print(c("─" * 50, "cyan"))
            print()
            print(c("  ═" * 25, "green"))
            print(c(f"  FINAL IDEA", "bold green"))
            print(c("  ═" * 25, "green"))
            print()
            print(f"  {event.content}")
            print()
            print(c("═" * 50, "cyan"))


if __name__ == "__main__":
    asyncio.run(main())