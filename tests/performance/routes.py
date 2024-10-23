from tests.constants import Endpoint
from tts.extensions import config_tts
from tts.helpers.constants import EnvironmentVariables


class Routes:
    """Locust routes for the external server."""

    def __init__(self, client):
        self.host = config_tts.resources.external_server_url
        self.client = client

    def health(self):
        """GET api/v1/health."""
        self.client.get(f"{self.host}/{Endpoint.HEALTH}")

    def main(self):
        """GET /."""
        self.client.get(self.host)

    def proxy_sentiment_analysis(self, data):
        """POST api/v1/sentiment-analysis."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": EnvironmentVariables.API_KEY,
        }
        self.client.options(
            f"{self.host}/{Endpoint.PROXY_SENTIMENT_ANALYSIS}",
            headers=headers,
        )
        self.client.post(
            f"{self.host}/{Endpoint.PROXY_SENTIMENT_ANALYSIS}",
            json=data,
            headers=headers,
        )
