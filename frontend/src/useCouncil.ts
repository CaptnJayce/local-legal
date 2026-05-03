import { useCallback, useEffect, useRef, useState } from "react";
import { type CouncilEvent, type ScoreCard, startSession } from "./api";

export interface Message {
  agent: string;
  content: string;
  round: number;
}

export interface IterationResult {
  round: number;
  scoreCard: ScoreCard;
  refinedIdea: string;
}

export function useCouncil() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState<Message | null>(null);
  const [results, setResults] = useState<IterationResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const pendingScoreRef = useRef<{ round: number; scoreCard: ScoreCard } | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const handleEvent = useCallback((event: CouncilEvent) => {
    switch (event.type) {
      case "chunk": {
        if (!event.agent || !event.content) return;
        const agent = event.agent;
        const content = event.content;
        setStreaming(prev =>
          prev?.agent === agent
            ? { ...prev, content: prev.content + content }
            : { agent, content, round: event.round }
        );
        break;
      }
      case "message": {
        if (!event.agent || !event.content || event.content === "Scoring...") return;
        const agent = event.agent;
        const content = event.content;
        setMessages(prev => [...prev, { agent, content, round: event.round }]);
        setStreaming(null);
        break;
      }
      case "score": {
        if (event.score_card) {
          pendingScoreRef.current = { round: event.round, scoreCard: event.score_card };
        }
        break;
      }
      case "refined": {
        if (!event.content || !pendingScoreRef.current) return;
        const { round, scoreCard } = pendingScoreRef.current;
        const refinedIdea = event.content;
        setResults(prev => [...prev, { round, scoreCard, refinedIdea }]);
        pendingScoreRef.current = null;
        break;
      }
      case "done": {
        setIsRunning(false);
        setStreaming(null);
        break;
      }
    }
  }, []);

  const submit = useCallback(async (idea: string, iterations: number, turns: number) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setMessages([]);
    setStreaming(null);
    setResults([]);
    setError(null);
    setIsRunning(true);
    pendingScoreRef.current = null;

    try {
      await startSession(
        { idea, iterations, turns_per_round: turns },
        handleEvent,
        abortRef.current.signal,
      );
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        setIsRunning(false);
        return;
      }
      setError(err instanceof Error ? err.message : "Unknown error");
      setIsRunning(false);
    }
  }, [handleEvent]);

  return { messages, streaming, results, isRunning, error, submit };
}
