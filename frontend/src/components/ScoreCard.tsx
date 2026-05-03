import type { ScoreCard as ScoreCardType } from "../api";

interface Props {
  scoreCard: ScoreCardType;
  round: number;
}

const dimensions = ["viability", "novelty", "risk", "potential"] as const;

export function ScoreCard({ scoreCard, round }: Props) {
  return (
    <div className="scorecard">
      <h3>Scorecard — Round {round}</h3>
      {dimensions.map(dim => {
        const { score, reasoning } = scoreCard[dim];
        return (
          <div key={dim} className="scorecard-row">
            <div className="scorecard-label">
              <span className="scorecard-dim">{dim}</span>
              <span className="scorecard-score">{score}/10</span>
            </div>
            <div className="scorecard-bar">
              <div className="scorecard-fill" style={{ width: `${score * 10}%` }} />
            </div>
            <p className="scorecard-reasoning">{reasoning}</p>
          </div>
        );
      })}
    </div>
  );
}
