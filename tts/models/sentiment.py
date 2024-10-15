from typing import Optional

from pydantic import BaseModel, Field, validator


class SentimentRequest(BaseModel):
    """Store JSON keys from the request."""

    process_text: bool
    text: str = Field(..., min_length=1, max_length=700)


class TransformersSentimentScores(BaseModel):
    """Model for transformer sentiment scores."""

    label: str
    score: float


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""

    text: str
    transformers_sentiment_scores: Optional[TransformersSentimentScores] = None
    vader_sentiment_scores: Optional[dict[str, float]] = None
    vader_sentiment_result: Optional[str] = None
    sentiment_result: Optional[str] = None

    @validator("vader_sentiment_result", pre=True, always=True)
    def calculate_sentiment_result(cls, v, values):  # noqa
        """Calculate overall sentiment based on VADER sentiment scores."""
        sentiment_scores = values.get("vader_sentiment_scores", {})
        compound = sentiment_scores.get("compound", 0)
        if compound > 0:
            return "positive"
        elif compound < 0:
            return "negative"
        else:
            return "neutral"
