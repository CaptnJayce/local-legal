interface Props {
  agent: string;
  content: string;
  round: number;
  isStreaming?: boolean;
}

const badgeColour: Record<string, string> = {
  Critic: "red",
  Appraiser: "green",
  Judge: "goldenrod",
};

export function AgentMessage({ agent, content, round, isStreaming = false }: Props) {
  return (
    <div className="agent-message">
      <div className="agent-message-header">
        <span
          className={`agent-badge${isStreaming ? " streaming" : ""}`}
          style={{ color: badgeColour[agent] ?? "white" }}
        >
          {agent}
        </span>
        <span className="agent-round">Round {round}</span>
      </div>
      <p className="agent-content">{content}</p>
    </div>
  );
}
