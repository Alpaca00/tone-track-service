import pytest
from requests.exceptions import RequestException, HTTPError

from tests.constants import Endpoint
from tts.helpers.constants import EnvironmentVariables


class TestSmokeApiRoutes:
    """Smoke test the API routes."""

    @pytest.mark.health_check_api
    def test_health_check(self, client):
        """Test the health check endpoint."""
        request = client.get(Endpoint.HEALTH, json_path="status")

        error_message = "The health endpoint did not return :: {}, check in the health_controller.py file."

        response_value, response_code = request

        assert response_code == 200, error_message.format(response_code)
        assert response_value == "up", error_message.format(response_value)

    @pytest.mark.parametrize(
        "sentiment_type, expected_result, endpoint",
        [
            ("vader", "negative", Endpoint.PROXY_SENTIMENT_ANALYSIS),
            ("transformer", "negative", Endpoint.PROXY_SENTIMENT_ANALYSIS),
            ("all", "negative", Endpoint.PROXY_SENTIMENT_ANALYSIS),
            ("vader", "negative", Endpoint.SENTIMENT_ANALYSIS),
            ("transformer", "negative", Endpoint.SENTIMENT_ANALYSIS),
            ("all", "negative", Endpoint.SENTIMENT_ANALYSIS),
        ],
        ids=[
            "vader_proxy",
            "transformer_proxy",
            "all_proxy",
            "vader_sentiment",
            "transformer_sentiment",
            "all_sentiment",
        ],
    )
    @pytest.mark.sentiment_analysis_api
    def test_sentiment_analysis_post(
        self, client, config, sentiment_type, expected_result, endpoint
    ):
        """Test the proxy sentiment analysis endpoint."""

        message_input = config.project.default_sentiment_message

        request = client.post(
            endpoint,
            json={"text": message_input, "sentiment_type": sentiment_type},
            headers={"Authorization": EnvironmentVariables.API_KEY},
        )

        error_message = "The sentiment analysis endpoint did not return {}, check in the sentiment_controller.py file."

        response_value, response_code = request

        assert response_code == 200, error_message.format(response_code)
        assert message_input == response_value["text"], error_message.format(
            message_input
        )
        assert (
            expected_result in response_value["sentiment_result"]
        ), error_message.format(expected_result)

    @pytest.mark.proxy_sentiment_analysis_options_api
    def test_proxy_sentiment_analysis_options(self, client):
        """Test the proxy sentiment analysis OPTIONS endpoint."""
        request = client.options(Endpoint.PROXY_SENTIMENT_ANALYSIS)

        response_value, response_code = request

        error_message_template = (
            "The proxy sentiment analysis OPTIONS endpoint did not return {}, "
            "check in the sentiment_controller.py file."
        )

        assert response_code == 204, error_message_template.format(response_code)

        expected_headers = {
            "Access-Control-Allow-Origin": True,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }

        for header, expected_value in expected_headers.items():
            if expected_value is True:
                assert header in response_value, error_message_template
            else:
                assert (
                    response_value[header] == expected_value
                ), error_message_template

    @pytest.mark.parametrize(
        "endpoint",
        [
            "events",
            "interactions",
            "commands",
            "verification",
        ],
        ids=[
            "events",
            "interactions",
            "commands",
            "verification",
        ],
    )
    @pytest.mark.slack_endpoints_api
    def test_slack_endpoints(self, client, endpoint):
        """Test the Slack endpoints."""
        try:
            client.post(f"api/v1/slack/{endpoint}")

        except RequestException as e:
            if isinstance(e, HTTPError):
                assert e.response.status_code == 403
                assert " UNAUTHORIZED" in e.response.json()["error"]
