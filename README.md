# local-legal

An LLM council that debates your ideas. Three agents — Critic, Appraiser, and Judge — argue a given idea across as many rounds as you want, score it, and produce a refined version.

## What it does

Bring an idea. The Critic looks for holes, the Appraiser fights back and builds it up, and the Judge scores and refines. Set iterations higher to run the improved idea back through the whole cycle — each pass tightens it further.

## Setup

### Prerequisites

- Python 3.11+
- [Bun](https://bun.sh)
- An LLM provider (see below)

### Install

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate      # fish: source .venv/bin/activate.fish
pip install -r requirements.txt

# Frontend
cd frontend
bun install
```

### Configure

Copy `.env.example` to `.env` and fill in the relevant values for your chosen provider. The app uses these as defaults — you can override them per-session from the settings panel.

## Run

```bash
# Backend (from repo root, with venv active)
PYTHONPATH=. uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
bun run dev
```

Open [http://localhost:5173](http://localhost:5173).

### CLI (no frontend)

```bash
PYTHONPATH=. python -m backend.council "your idea here" --iterations 1 --turns 3
```

`--iterations` — how many full cycles to run. Each one refines the idea further.  
`--turns` — back-and-forth exchanges between Critic and Appraiser per cycle.

## LLM Providers

Switch providers from the settings panel in the UI, or by editing `PROVIDER` and `MODEL` in `.env`.

---

### Ollama (default — local, free, private)

Runs on your machine. No API key, no cost, nothing leaves your network.

**Install:** [ollama.com](https://ollama.com)

**Pull a model:**

```bash
ollama pull llama3.1
```

**Recommended models for 8GB VRAM:**

| Model        | Params | VRAM  | Notes           |
| ------------ | ------ | ----- | --------------- |
| `llama3.1`   | 8B     | ~6GB  | Tested, default |
| `mistral`    | 7B     | ~5GB  | Fast            |
| `gemma2`     | 9B     | ~8GB  | Good reasoning  |

No API key needed. Set `PROVIDER=ollama` and `MODEL=llama3.1` in `.env`.

---

### OpenRouter

Routes to hundreds of models through one API key. Good if you want to try different cloud models without signing up everywhere, or just don't want to run things locally.

**Get a key:** [openrouter.ai/keys](https://openrouter.ai/keys)

**Recommended models for testing:**

| Model                      | Notes                        |
| -------------------------- | ---------------------------- |
| `openai/gpt-4o-mini`       | Fast and cheap, good default |
| `anthropic/claude-haiku-4` | Strong reasoning, low cost   |
| `google/gemini-flash-1.5`  | Very fast                    |

Set `PROVIDER=openrouter`, `MODEL=openai/gpt-4o-mini`, and `OPENROUTER_API_KEY=<your key>` in `.env`.

In the UI, enter your key in the API Key field after selecting OpenRouter. It stays in the browser and only goes to the backend when you start a session.

---

### Anthropic

Direct access to Claude. Worth it if you're mostly using Claude anyway — skips the OpenRouter hop.

**Get a key:** [console.anthropic.com](https://console.anthropic.com)

**Recommended models:**

| Model                        | Notes                            |
| ---------------------------- | -------------------------------- |
| `claude-3-5-haiku-20241022`  | Fast, cheap, good for iteration  |
| `claude-sonnet-4-6`          | Better reasoning, higher cost    |

Set `PROVIDER=anthropic`, `MODEL=claude-3-5-haiku-20241022`, and `ANTHROPIC_API_KEY=<your key>` in `.env`.

In the UI, enter your key in the API Key field after selecting Anthropic. Same as above — stays local, only used per session.

---

## Hardware note

Tested locally on an 8GB VRAM GPU. Models above that limit are untested. If you're on lower-end hardware, use a cloud provider — OpenRouter's cheapest models cost fractions of a cent per debate.

## Future

- `claude-opus-4` — when hardware allows
- Session history (SQLite)
- Docker packaging
