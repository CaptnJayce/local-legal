import os

import litellm

from backend.config import settings

if settings.ollama_base_url:
    os.environ["OLLAMA_BASE_URL"] = settings.ollama_base_url
if settings.openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key
if settings.anthropic_api_key:
    os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key


async def call_llm(messages: list[dict], system: str) -> str:

    full_messages = [{"role": "system", "content": system}] + messages

    model = f"{settings.provider}/{settings.model}"

    response = await litellm.acompletion(
        model=model,
        messages=full_messages,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty response")
    return content