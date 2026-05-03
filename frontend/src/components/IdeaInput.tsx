import { type FormEvent, useState } from "react";

interface Props {
  onSubmit: (idea: string, iterations: number, turns: number) => void;
  isRunning: boolean;
}

export function IdeaInput({ onSubmit, isRunning }: Props) {
  const [idea, setIdea] = useState("");
  const [iterations, setIterations] = useState(1);
  const [turns, setTurns] = useState(3);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = idea.trim();
    if (!trimmed) return;
    onSubmit(trimmed, iterations, turns);
  }

  const canSubmit = !isRunning && idea.trim().length > 0;

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={idea}
        onChange={e => setIdea(e.target.value)}
        placeholder="Describe your idea..."
        disabled={isRunning}
        rows={4}
      />
      <label>
        Iterations
        <input
          type="number"
          min={1}
          max={10}
          value={iterations}
          onChange={e => setIterations(Number(e.target.value))}
          disabled={isRunning}
        />
      </label>
      <label>
        Turns per round
        <input
          type="number"
          min={1}
          max={10}
          value={turns}
          onChange={e => setTurns(Number(e.target.value))}
          disabled={isRunning}
        />
      </label>
      <button type="submit" disabled={!canSubmit}>
        {isRunning ? "Running..." : "Submit"}
      </button>
    </form>
  );
}
