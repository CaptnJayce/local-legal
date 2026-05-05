import { useCallback, useEffect, useState } from "react";
import { useCouncil } from "./useCouncil";
import { useSettings } from "./useSettings";
import { type ServerConfig, getConfig } from "./api";
import { IdeaInput } from "./components/IdeaInput";
import { CouncilRoom } from "./components/CouncilRoom";
import { ScoreCard } from "./components/ScoreCard";
import { RefinedIdea } from "./components/RefinedIdea";
import { IterationTimeline } from "./components/IterationTimeline";
import { Settings } from "./components/Settings";
import "./App.css";

export default function App() {
  const { messages, streaming, results, originalIdea, isRunning, error, submit } = useCouncil();
  const { provider, model, apiKey, update } = useSettings();
  const [serverConfig, setServerConfig] = useState<ServerConfig | null>(null);

  useEffect(() => {
    getConfig().then(setServerConfig).catch(() => {});
  }, []);

  const handleSubmit = useCallback(
    (idea: string, iterations: number, turns: number) =>
      submit(idea, iterations, turns, { provider, model, apiKey }),
    [submit, provider, model, apiKey],
  );

  return (
    <div className="app">
      <header>
        <h1>Local Legal</h1>
        {serverConfig && (
          <span className="header-config">{serverConfig.provider} / {serverConfig.model}</span>
        )}
      </header>
      <div className="layout">
        <aside className="sidebar">
          <Settings
            settings={{ provider, model, apiKey }}
            onChange={update}
          />
        </aside>
        <main>
          <IdeaInput onSubmit={handleSubmit} isRunning={isRunning} />
          {error && <p className="error">{error}</p>}
          {(messages.length > 0 || streaming) && (
            <CouncilRoom messages={messages} streaming={streaming} />
          )}
          {results.map(result => (
            <div key={result.round} className="iteration-result">
              <ScoreCard scoreCard={result.scoreCard} round={result.round} />
              <RefinedIdea idea={result.refinedIdea} round={result.round} />
            </div>
          ))}
          {results.length > 1 && originalIdea && (
            <IterationTimeline originalIdea={originalIdea} results={results} />
          )}
        </main>
      </div>
    </div>
  );
}
