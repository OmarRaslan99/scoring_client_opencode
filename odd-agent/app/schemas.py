from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class WebSearchResult(BaseModel):
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    content: str = ""


class MoralScoreResult(BaseModel):
    found: bool
    url: str
    global_score: int | None = None
    summary: str = ""


class ODDScore(BaseModel):
    odd_number: int = Field(ge=1, le=17)
    score: int = Field(ge=-1, le=3)
    confidence: int = Field(ge=0, le=100)
    explanation: str | None = None

    @model_validator(mode="after")
    def validate_explanation(self) -> "ODDScore":
        if self.score == 0:
            self.explanation = None
            return self
        if not self.explanation or not self.explanation.strip():
            raise ValueError("explanation is required when score is not 0")
        self.explanation = self.explanation.strip()
        return self


class ODDScoreResponse(BaseModel):
    scores: list[ODDScore] = Field(min_length=17, max_length=17)

    @model_validator(mode="after")
    def validate_odd_coverage(self) -> "ODDScoreResponse":
        odd_numbers = [score.odd_number for score in self.scores]
        if sorted(odd_numbers) != list(range(1, 18)):
            raise ValueError("scores must contain exactly one entry for each ODD from 1 to 17")
        self.scores = sorted(self.scores, key=lambda item: item.odd_number)
        return self