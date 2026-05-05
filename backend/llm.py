import os
from typing import AsyncGenerator

import litellm

from backend.config import settings

if settings.ollama_base_url:
    os.environ["OLLAMA_BASE_URL"] = settings.ollama_base_url
if settings.openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key


def _resolve_model(provider: str | None, model: str | None) -> str:
    return f"{provider or settings.provider}/{model or settings.model}"


async def call_llm(
    messages: list[dict],
    system: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    full_messages = [{"role": "system", "content": system}] + messages
    kwargs: dict = {"model": _resolve_model(provider, model), "messages": full_messages}
    if api_key:
        kwargs["api_key"] = api_key

    response = await litellm.acompletion(**kwargs)

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty response")
    return content


async def stream_llm(
    messages: list[dict],
    system: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> AsyncGenerator[str, None]:
    full_messages = [{"role": "system", "content": system}] + messages
    kwargs: dict = {"model": _resolve_model(provider, model), "messages": full_messages, "stream": True}
    if api_key:
        kwargs["api_key"] = api_key

    response = await litellm.acompletion(**kwargs)

    async for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
