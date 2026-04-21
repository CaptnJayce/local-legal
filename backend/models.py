from pydantic import BaseModel, Field


class DebateMessage(BaseModel):
    agent: str
    role: str
    content: str
    round: int


class ScoreDimension(BaseModel):
    score: int = Field(ge=1, le=10)
    reasoning: str


class ScoreCard(BaseModel):
    viability: ScoreDimension
    novelty: ScoreDimension
    risk: ScoreDimension
    potential: ScoreDimension


class Verdict(BaseModel):
    score_card: ScoreCard
    refined_idea: str
    summary: str


class CouncilResult(BaseModel):
    original_idea: str
    iterations: list[Verdict]