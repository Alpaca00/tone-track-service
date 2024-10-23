import pytest
from flask.testing import FlaskClient

from tests.constants import Endpoint
from tests.unittest.conftest import MockSentimentRequest, MockSentimentResponse


@pytest.mark.sentiment_analysis_unittest
def test_sentiment_analysis_valid_input(client, mock_nltk, config_project):
    """Test the sentiment analysis with valid input."""
    response = client.post(
        Endpoint.SENTIMENT_ANALYSIS,
        json={
            "text": MockSentimentRequest().text,
            "sentiment_type": config_project.sentiment_type,
        },
    )

    actual_result = response.get_json()
    expected_result = MockSentimentResponse(
        MockSentimentRequest().text
    ).model_dump_json()

    assert response.status_code == 200
    assert actual_result == expected_result


@pytest.mark.sentiment_analysis_unittest
@pytest.mark.parametrize(
    "text",
    [
        "",
        "Limit the text to 700 characters" * 100,
    ],
    ids=["empty_text", "long_text"],
)
def test_sentiment_analysis_invalid_input(
    client: FlaskClient, text, config_project
):
    """Test the sentiment analysis with invalid input."""
    response = client.post(
        Endpoint.SENTIMENT_ANALYSIS,
        json={"text": text, "sentiment_type": config_project.sentiment_type},
    )
    json_data = response.get_json()

    assert response.status_code == 422 and "error" in json_data


@pytest.mark.sentiment_analysis_unittest
def test_sentiment_analysis_internal_error(client: FlaskClient, config_project):
    """Test the sentiment analysis to ensure it handles internal errors."""
    response = client.post(
        Endpoint.SENTIMENT_ANALYSIS,
        json={
            "invalid_field": "Some text",
            "sentiment_type": config_project.sentiment_type,
        },
    )
    json_data = response.get_json()

    assert response.status_code == 422 and "error" in json_data
