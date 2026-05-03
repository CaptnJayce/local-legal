export interface ScoreDimension {
  score: number;
  reasoning: string;
}

export interface ScoreCard {
  viability: ScoreDimension;
  novelty: ScoreDimension;
  risk: ScoreDimension;
  potential: ScoreDimension;
}

export type CouncilEventType = "chunk" | "message" | "score" | "refined" | "done";

export interface CouncilEvent {
  type: CouncilEventType;
  agent: string | null;
  content: string | null;
  round: number;
  score_card: ScoreCard | null;
}

export interface SessionRequest {
  idea: string;
  iterations: number;
  turns_per_round: number;
}

const API_BASE = "http://localhost:8000";
const SSE_PREFIX = "data: ";

export async function startSession(
  req: SessionRequest,
  onEvent: (event: CouncilEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) throw new Error(`Session failed: ${res.status}`);
  if (!res.body) throw new Error("Response body is null");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split("\n\n");
      buffer = parts.pop()!;

      for (const part of parts) {
        const line = part.trim();
        if (!line.startsWith(SSE_PREFIX)) continue;
        try {
          onEvent(JSON.parse(line.slice(SSE_PREFIX.length)) as CouncilEvent);
        } catch {
          // skip malformed events
        }
      }
    }

    buffer += decoder.decode();
  } finally {
    reader.cancel().catch(() => {});
  }
}
