from backend.agents.base import BaseAgent
from backend.llm import call_llm
from backend.models import DebateMessage

_JSON_TEMPLATE = """\
Output ONLY the following JSON with your scores filled in. No other text.

{
  "score_card": {
    "viability": {"score": <1-10>, "reasoning": "<one sentence>"},
    "novelty":   {"score": <1-10>, "reasoning": "<one sentence>"},
    "risk":      {"score": <1-10>, "reasoning": "<one sentence>"},
    "potential": {"score": <1-10>, "reasoning": "<one sentence>"}
  },
  "refined_idea": "<improved idea as a single paragraph>",
  "summary": "<2-3 sentence verdict>"
}"""


class Judge(BaseAgent):
    name = "Judge"
    system_prompt = "You are the Judge in a debate council. You score ideas honestly and output only valid JSON."

    async def respond(self, idea: str, history: list[DebateMessage]) -> str:
        messages = self._build_messages(idea, history)
        messages[-1]["content"] += f"\n\n{_JSON_TEMPLATE}"
        return await call_llm(messages, self.system_prompt)
