# Project: local-legal

AI council that debates ideas via Critic, Appraiser, and Judge agents.

## Stack

- Backend: Python, FastAPI, LiteLLM, Pydantic
- Frontend: TypeScript, React, Vite, Bun

## Conventions

- Async everywhere in backend
- Pydantic models for all data structures
- Streaming-first design (SSE)
- Never hardcode API keys — always .env

## Do not touch

- .env files
- Any file not relevant to the current task

## Current phase

Phase 6 complete. Phase 7 next (settings & provider config UX).
