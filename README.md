# local-legal

A local LLM council made to thoroughly critique ideas you bring them, providing scores, appraisals, & criticisms. Run locally or with LLM providers.

## What it does

You bring an idea. Three AI agents — Critic, Appraiser, and Judge — debate it in rounds. The Critic stress-tests it, the Appraiser counters and strengthens it, and the Judge scores it and produces a refined version. After however many rounds you want, you get scores and a stronger idea.

## Run it

```bash
# Activate the venv
source .venv/bin/activate

# Run a debate
PYTHONPATH=. python -m backend.council "your idea here" --iterations 1 --turns 3
```

`--iterations` — how many times the whole cycle repeats (more iterations = more refined the idea becomes).
`--turns` — how many back-and-forth exchanges between Critic and Appraiser per round.

## Important Note

I don't have the greatest hardware - if you're a big AI enthusiast you likely have your own homelab. I have one GPU for gaming at 8GB VRAM, so tested local models are extremely limited.

## LLM Providers

Change providers by modifying `PROVIDER` and `MODEL` in `.env`.

### Ollama (local, default)

Runs entirely on your machine — no API costs, no network, private.

Requires [Ollama](https://ollama.com) installed and a model pulled:

```
ollama pull llama3.1
```

| Model      | Params | VRAM | Notes    |
| ---------- | ------ | ---- | -------- |
| `llama3.1` | 8B     | ~6GB | Tested ✓ |

### OpenRouter

Requires `OPENROUTER_API_KEY` in `.env`.

| Model                | Notes   |
| -------------------- | ------- |
| `openai/gpt-4o-mini` | Testing |

### Anthropic

Requires `ANTHROPIC_API_KEY` in `.env`.

| Model              | Notes   |
| ------------------ | ------- |
| `claude-3-5-haiku` | Testing |

## Future Models

Planned additions pending better hardware.

- `claude-sonnet-4.6` (Anthropic) — next-tier reasoning
