interface Props {
  idea: string;
  round: number;
}

export function RefinedIdea({ idea, round }: Props) {
  return (
    <div className="refined-idea">
      <h3>Refined Idea — Round {round}</h3>
      <p>{idea}</p>
    </div>
  );
}
