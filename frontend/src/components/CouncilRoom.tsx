import { useEffect, useRef } from "react";
import type { Message } from "../useCouncil";
import { AgentMessage } from "./AgentMessage";

interface Props {
  messages: Message[];
  streaming: Message | null;
}

export function CouncilRoom({ messages, streaming }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming]);

  return (
    <div className="council-room">
      {messages.map((msg, i) => (
        <AgentMessage
          key={`${msg.round}-${msg.agent}-${i}`}
          agent={msg.agent}
          content={msg.content}
          round={msg.round}
        />
      ))}
      {streaming && (
        <AgentMessage
          agent={streaming.agent}
          content={streaming.content}
          round={streaming.round}
          isStreaming
        />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
