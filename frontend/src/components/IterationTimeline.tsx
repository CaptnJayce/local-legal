import { type IterationResult } from "../useCouncil";

interface Props {
  originalIdea: string;
  results: IterationResult[];
}

export function IterationTimeline({ originalIdea, results }: Props) {
  const steps = [
    { label: "Original", text: originalIdea },
    ...results.map(r => ({ label: `Iteration ${r.round}`, text: r.refinedIdea })),
  ];

  return (
    <div className="timeline">
      <h3 className="timeline-heading">Idea Progression</h3>
      {steps.map((step, i) => (
        <div key={step.label} className="timeline-step">
          <div className="timeline-marker">
            <span className="timeline-dot" />
            {i < steps.length - 1 && <span className="timeline-line" />}
          </div>
          <div className="timeline-content">
            <span className="timeline-label">{step.label}</span>
            <p className="timeline-text">{step.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
