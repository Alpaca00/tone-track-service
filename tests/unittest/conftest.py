from unittest.mock import MagicMock
import pytest

from tts.app import SentimentAnalysisService
from tts.extensions import config_tts
from tts.helpers.constants import EnvironmentVariables


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
    return config_tts.project


class PrepareSentimentRequest:
    """Prepare the sentiment request."""

    def __init__(
        self,
        text: str = "Hello from the mock!",
        sentiment_type: str = "vader",
    ) -> None:
        self.text = text
        self.sentiment_type = sentiment_type
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": EnvironmentVariables.API_KEY,
        }

    def model_dump_json(self) -> dict[str, any]:
        """Return the model as a dictionary."""
        return {"text": self.text, "sentiment_type": self.sentiment_type}


class PrepareSentimentResponse:
    """Prepare the sentiment response."""

    def __init__(
        self,
        text: str = "Hello from the mock!",
        sentiment_result: str = "not negative",
    ) -> None:
        self.text = text
        self.sentiment_result = sentiment_result

    def model_dump_json(self) -> dict[str, any]:
        """Return the model as a dictionary."""
        return {"text": self.text, "sentiment_result": self.sentiment_result}


class MockSentimentScores:
    """Mock the sentiment scores from the VADER model."""

    def __init__(self):
        self.vader_scores = {
            "neg": 0.0,
            "neu": 0.543,
            "pos": 0.457,
            "compound": 0.6369,
        }

    def vader_model(self) -> tuple:
        """Return the VADER model."""
        return None, self.vader_scores


@pytest.fixture(scope="function")
def mock_nltk(monkeypatch):
    """Mock the SentimentIntensityAnalyzer."""
    mock_analyzer = MagicMock()

    mock_analyzer.return_value = MockSentimentScores().vader_model()
    monkeypatch.setattr(
        "tts.helpers.functions.get_sentiment_scores",
        mock_analyzer,
    )
