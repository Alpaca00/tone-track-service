import pytest
from flask.testing import FlaskClient

from tests.unittest.conftest import MockSentimentRequest, MockSentimentResponse


@pytest.mark.sentiment_analysis
def test_sentiment_analysis_valid_input(client, mock_nltk):
    """Test the sentiment analysis with valid input."""
    response = client.post(
        "/api/v1/sentiment-analysis",
        json={"text": MockSentimentRequest().text, "process_text": True},
    )

    actual_result = response.get_json()
    expected_result = MockSentimentResponse(
        MockSentimentRequest().text
    ).model_dump_json()

    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.sentiment_analysis
@pytest.mark.parametrize(
    "text",
    [
        "",
        "Limit the text to 700 characters" * 100,
    ],
    ids=["empty_text", "long_text"],
)
def test_sentiment_analysis_invalid_input(client: FlaskClient, text):
    """Test the sentiment analysis with invalid input."""
    response = client.post(
        "/api/v1/sentiment-analysis", json={"text": text, "process_text": True}
    )
    json_data = response.get_json()

    assert response.status_code == 422 and "error" in json_data


@pytest.mark.sentiment_analysis
def test_sentiment_analysis_internal_error(client: FlaskClient):
    """Test the sentiment analysis to ensure it handles internal errors."""
    response = client.post(
        "/api/v1/sentiment-analysis",
        json={"invalid_field": "Some text", "process_text": True},
    )
    json_data = response.get_json()

    assert response.status_code == 422 and "error" in json_data
