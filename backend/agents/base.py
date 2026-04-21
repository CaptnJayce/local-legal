from typing import AsyncGenerator

from backend.llm import call_llm, stream_llm
from backend.models import DebateMessage


class BaseAgent:
    name: str
    system_prompt: str

    async def respond(self, idea: str, history: list[DebateMessage]) -> str:
        messages = self._build_messages(idea, history)
        return await call_llm(messages, self.system_prompt)

    async def stream_respond(
        self, idea: str, history: list[DebateMessage]
    ) -> AsyncGenerator[str, None]:
        messages = self._build_messages(idea, history)
        async for chunk in stream_llm(messages, self.system_prompt):
            yield chunk

    def _build_messages(self, idea: str, history: list[DebateMessage]) -> list[dict]:
        messages = []

        if history:
            for msg in history:
                messages.append({
                    "role": "user",
                    "content": self._format_message(msg),
                })

        messages.append({
            "role": "user",
            "content": f"Current idea under discussion: {idea}",
        })

        return messages

    def _format_message(self, msg: DebateMessage) -> str:
        return f"[{msg.agent}] (Round {msg.round}): {msg.content}"