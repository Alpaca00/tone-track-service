from unittest.mock import MagicMock
import pytest

from tts.app import SentimentAnalysisService
from tts.helpers.functions import Config


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = SentimentAnalysisService(environment="testing").app
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def config_project():
    """Return the configuration."""
    config = Config()
    return config.project


class MockSentimentRequest:
    """Mock the SentimentRequest model."""

    def __init__(self, text: str = "Hello from the mock!") -> None:
        self.text = text

    def model_dump_json(self) -> dict[str, any]:
        """Return the model as a dictionary."""
        return {"text": self.text}


class MockSentimentResponse:
    """Mock the SentimentResponse model."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.sentiment_scores = {
            "neg": 0.0,
            "neu": 0.543,
            "pos": 0.457,
            "compound": 0.6369,
        }
        self.overall_sentiment = "positive"

    def model_dump_json(self) -> dict[str, any]:
        """Return the model as a dictionary."""
        return {
            "text": self.text,
            "sentiment_scores": self.sentiment_scores,
            "overall_sentiment": self.overall_sentiment,
        }


@pytest.fixture(scope="function")
def mock_nltk(monkeypatch):
    """Mock the SentimentIntensityAnalyzer."""
    mock_analyzer = MagicMock()

    mock_analyzer.return_value = MockSentimentResponse(
        MockSentimentRequest().text
    ).model_dump_json()
    monkeypatch.setattr(
        "tts.models.sentiment.SentimentResponse.model_dump_json",
        mock_analyzer,
    )
