from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.config import settings
from backend.council import Council

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "provider": settings.provider, "model": settings.model}


@app.get("/config")
async def config():
    return {"provider": settings.provider, "model": settings.model}


class SessionRequest(BaseModel):
    idea: str
    iterations: int = 1
    turns_per_round: int = 3
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None


@app.post("/session")
async def session(body: SessionRequest):
    council = Council()

    async def generate():
        async for event in council.run(
            body.idea,
            body.iterations,
            body.turns_per_round,
            provider=body.provider,
            model=body.model,
            api_key=body.api_key,
        ):
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
