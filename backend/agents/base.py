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
        content = f"Idea under discussion: {idea}"
        if history:
            history_block = "\n\n".join(
                f"[{msg.agent} — Round {msg.round}]: {msg.content}"
                for msg in history
            )
            content += f"\n\nDebate so far:\n{history_block}"
        return [{"role": "user", "content": content}]