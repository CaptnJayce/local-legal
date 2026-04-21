# local-legal — TODO

A step-by-step build guide. Work through phases in order.

**Stack:** Python (FastAPI + LiteLLM) · TypeScript (React + Vite)  
**Default runtime:** Ollama (local) · **Cloud providers:** OpenRouter, Anthropic

---

## Phase 1 — Project scaffold

> Get the repo, folder structure, and tooling in place before writing any logic.

- [x] Clone the repo locally
  - `git clone git@github.com:CaptnJayce/local-legal.git`
- [x] Create top-level folders
  - `mkdir backend frontend`
- [x] Set up Python virtual environment in `backend/`
  - `python -m venv .venv && source .venv/bin/activate`
- [x] Install core backend dependencies
  - `pip install fastapi uvicorn litellm pydantic python-dotenv`
- [x] Scaffold React + Vite app in `frontend/`
  - `bun create vite frontend --template react-ts`
- [x] Add a root `.gitignore` covering `.venv`, `node_modules`, `.env`, `__pycache__`, `bun.lockb`
- [x] Write a minimal README with project overview and local setup steps

---

## Phase 2 — LLM provider abstraction

> Wire up LiteLLM so Ollama is the default and OpenRouter/Anthropic are drop-in alternatives.
> The goal: swap providers with a config change, no code changes.

- [x] Install Ollama and pull a model that fits in 8GB VRAM
  - `ollama pull llama3.1` (8B — good default) or `ollama pull mistral`
- [x] Create `backend/config.py` — load provider settings from `.env`
  - Required vars: `PROVIDER`, `MODEL`, and optionally `OLLAMA_BASE_URL`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`
  - Default: `PROVIDER=ollama`, `MODEL=llama3.1`
- [x] Write `backend/llm.py` — a thin async wrapper around `litellm.acompletion()`
  - One function: `call_llm(messages: list, system: str) → str`
  - LiteLLM handles routing: `ollama/llama3.1`, `openrouter/...`, `anthropic/claude-...`
- [x] Smoke test the wrapper against Ollama
  - Print a response to a simple prompt, confirm it works
- [x] Smoke test the same wrapper against OpenRouter by swapping env vars
  - `PROVIDER=openrouter`, `MODEL=openai/gpt-4o-mini`, `OPENROUTER_API_KEY=...`
- [x] Smoke test against Anthropic
  - `PROVIDER=anthropic`, `MODEL=claude-3-5-haiku-20241022`, `ANTHROPIC_API_KEY=...`
- [x] Document model recommendations per provider in the README
  - Ollama: llama3.1 8B, mistral 7B, gemma2 9B (all fit in 8GB VRAM)
  - OpenRouter: any model — good for testing without local hardware
  - Anthropic: claude-3-5-haiku (fast + cheap for iteration)

---

## Phase 3 — Agents

> Build the three agents as Python classes. Test them standalone before wiring to the council.

- [x] Create `backend/agents/base.py` — `BaseAgent` with `name`, `system_prompt`, `respond()`
  - `respond(idea: str, history: list[DebateMessage]) → str`
  - Calls `call_llm()` internally with the agent's system prompt + full debate history
- [x] Create `backend/agents/critic.py` — adversarial persona
  - Forcefully argues against the idea, finds flaws, stress-tests assumptions
  - Should reference specific weaknesses rather than giving generic criticism
- [x] Create `backend/agents/appraiser.py` — advocate persona
  - Argues for the idea's merit, counters the Critic's specific points directly
  - Should not ignore what the Critic said — engage with it
- [x] Create `backend/agents/judge.py` — observer/synthesiser persona
  - Only called once at the end of each debate round, never during back-and-forth
  - Produces a `ScoreCard` and a refined version of the idea
- [x] Define Pydantic models in `backend/models.py`
  - `DebateMessage`: `agent`, `role`, `content`, `round`
  - `ScoreCard`: `viability`, `novelty`, `risk`, `potential` (each 1–10 + one-line reasoning)
  - `Verdict`: `score_card`, `refined_idea`, `summary`
  - `CouncilResult`: `original_idea`, `iterations: list[Verdict]`
- [x] Unit test each agent in isolation — just a plain Python script, print the outputs
  - Confirm the Critic and Appraiser respond differently in tone and stance

---

## Phase 4 — Council orchestrator

> Wire the agents into a debate loop. This is the core of the project.

- [ ] Create `backend/council.py` — `Council` class that owns all three agents
- [ ] Implement `run(idea: str, iterations: int, turns_per_round: int) → AsyncGenerator`
  - Outer loop: runs `iterations` times, feeding the refined idea back each time
  - Inner loop: Critic → Appraiser → repeat `turns_per_round` times
  - After inner loop: Judge scores and produces a refined idea
  - Yield each event as it happens (streaming-first design)
- [ ] Define the event schema yielded by the generator
  - `{ type: "message" | "score" | "refined" | "done", agent: str, content: str, round: int }`
- [ ] Add streaming support — use `litellm` with `stream=True`, yield chunks incrementally
  - Yield partial content as it arrives, don't wait for the full response
- [ ] Test end-to-end in a standalone script
  - `python -m backend.council "my idea here" --iterations 2 --turns 3`
  - Read through the full output and check the debate feels coherent

---

## Phase 5 — FastAPI backend

> Expose the council as a streaming HTTP API.

- [ ] Create `backend/main.py` with a FastAPI app
- [ ] Add `GET /health` — returns `{ status: "ok", provider: "...", model: "..." }`
- [ ] Add `POST /session` — accepts `{ idea, iterations, turns_per_round }`
  - Returns a `StreamingResponse` using Server-Sent Events (SSE)
  - Each SSE event is one JSON object matching the event schema from Phase 4
- [ ] Add CORS middleware
  - Allow `http://localhost:5173` (Vite dev server) in development
- [ ] Add `GET /config` — returns current provider and model (no keys) so the frontend can display it
- [ ] Test the stream endpoint with curl
  - `curl -N -X POST http://localhost:8000/session -H "Content-Type: application/json" -d '{"idea":"a subscription box for hackers","iterations":1,"turns_per_round":3}'`

---

## Phase 6 — React frontend

> Build the UI. Stream the debate in real time, display scores and the refined idea.

- [ ] Set up a typed API client in `frontend/src/api.ts`
  - Wraps `EventSource`, parses each SSE event, returns typed objects
- [ ] Write `useCouncil()` hook
  - Opens `EventSource` to `/session` on submit
  - Accumulates messages, scores, and refined idea in state
  - Exposes `messages`, `verdict`, `isRunning`, `submit(idea, iterations, turns)`
- [ ] Build `IdeaInput` component
  - Textarea for the idea, number inputs for iterations and turns per round, submit button
  - Disable inputs while a session is running
- [ ] Build `AgentMessage` component
  - Renders one debate message: agent name badge, content, round indicator
  - Critic = red badge, Appraiser = green, Judge = amber
- [ ] Build `CouncilRoom` component
  - Scrolling list of `AgentMessage` components
  - Auto-scrolls to bottom as messages stream in
  - Shows a "thinking" indicator (pulsing agent name) while awaiting a response
- [ ] Build `ScoreCard` component
  - Displays the four Judge scores with a bar or number per dimension
  - Shows the one-line reasoning for each score
- [ ] Build `RefinedIdea` component
  - Displays the improved idea text from each iteration
  - Visually distinct — this is the headline output of each round
- [ ] Wire everything together in `App.tsx`
- [ ] Add an iteration timeline if multiple iterations were run
  - Let the user compare original idea → iteration 1 → iteration 2 etc.

---

## Phase 7 — Settings & provider config UX

> Let users switch providers and enter API keys without touching code.

- [ ] Add a Settings panel to the frontend
  - Provider selector: Ollama (default) / OpenRouter / Anthropic
  - Model name text input (pre-filled with a sensible default per provider)
  - API key input (hidden, only shown for OpenRouter and Anthropic)
  - Turns per round number input with a note that more turns = slower + more tokens
- [ ] Store settings in `localStorage`
- [ ] Pass provider/model/key as request headers or body fields to `/session`
- [ ] Update the backend to accept per-request provider overrides
  - Falls back to env vars if the request doesn't include them
- [ ] Show current provider/model in the UI header (pulled from `GET /config`)
- [ ] Write provider setup sections in the README
  - **Ollama (default):** install guide, recommended models for 8GB VRAM, no API key needed
  - **OpenRouter:** where to get a key, recommended cheap models for testing
  - **Anthropic:** where to get a key, recommended model (haiku for speed/cost)

---

## Phase 8 — Packaging

> Make it easy for anyone to run the project with minimal setup.

- [ ] Write `docker-compose.yml`
  - `backend` service: FastAPI on port 8000
  - `frontend` service: nginx serving the React build on port 3000
  - `ollama` service (optional profile): for users who want fully local with no manual Ollama install
  - `docker compose up` should be the only command needed
- [ ] Write `backend/Dockerfile`
  - `FROM python:3.12-slim`, copy `backend/`, pip install, uvicorn entrypoint
- [ ] Write `frontend/Dockerfile`
  - Bun build stage + nginx serving `dist/`
- [ ] Add a `config.yaml.example` file users can copy to `config.yaml`
  - Documents every setting with comments, safe to commit (no real keys)
- [ ] Test the full Docker stack from a clean state
  - Remove all local state, `docker compose up`, verify the full flow works end-to-end
- [ ] _(Optional — v2)_ Explore Tauri for a native desktop app
  - Wraps the React frontend, bundles the Python backend
  - Produces `.exe`, `.dmg`, `.AppImage` — double-click to run, no terminal needed

---

## Phase 9 — Polish & release

- [ ] Add proper error handling throughout
  - Failed LLM calls (timeout, bad key, model not found)
  - Ollama not running or model not pulled
  - Network drops mid-stream
  - Display errors clearly in the UI, not just console logs
- [ ] Add session history — let users revisit past council sessions
  - SQLite via SQLModel is the lightest option
  - Store `CouncilResult` objects, list them in a sidebar
- [ ] Write `CONTRIBUTING.md`
- [ ] Add `LICENSE` (MIT recommended for open source)
- [ ] Final README pass
  - Quickstart (Docker and manual)
  - Provider config guide
  - Screenshots or a short demo GIF
  - Architecture overview (the three agents, the debate loop, the iteration cycle)
- [ ] Tag `v0.1.0` and push
  - `git tag v0.1.0 && git push origin v0.1.0`
