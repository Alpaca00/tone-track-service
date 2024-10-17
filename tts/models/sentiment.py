from typing import Literal

from pydantic import BaseModel, Field, validator


class SentimentRequest(BaseModel):
    """Store JSON keys from the request."""

    sentiment_type: Literal["vader", "transformer", "all"]
    text: str = Field(..., min_length=1, max_length=700)


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""

    text: str
    sentiment_result: str
