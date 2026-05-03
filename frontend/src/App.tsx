import { useCouncil } from "./useCouncil";
import { IdeaInput } from "./components/IdeaInput";
import { CouncilRoom } from "./components/CouncilRoom";
import { ScoreCard } from "./components/ScoreCard";
import { RefinedIdea } from "./components/RefinedIdea";
import "./App.css";

export default function App() {
  const { messages, streaming, results, isRunning, error, submit } = useCouncil();

  return (
    <div className="app">
      <header>
        <h1>Local Legal</h1>
      </header>
      <main>
        <IdeaInput onSubmit={submit} isRunning={isRunning} />
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
      </main>
    </div>
  );
}
