from typing import AsyncGenerator

from backend.llm import call_llm, stream_llm
from backend.models import DebateMessage


class BaseAgent:
    name: str
    system_prompt: str

    async def respond(
        self,
        idea: str,
        history: list[DebateMessage],
        *,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> str:
        messages = self._build_messages(idea, history)
        return await call_llm(messages, self.system_prompt, provider=provider, model=model, api_key=api_key)

    async def stream_respond(
        self,
        idea: str,
        history: list[DebateMessage],
        *,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> AsyncGenerator[str, None]:
        messages = self._build_messages(idea, history)
        async for chunk in stream_llm(messages, self.system_prompt, provider=provider, model=model, api_key=api_key):
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
