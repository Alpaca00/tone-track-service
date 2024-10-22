from flask import Blueprint, request, jsonify, current_app

from tts.helpers.constants import EnvironmentVariables
from tts.helpers.decorators import (
    handle_exceptions,
    require_api_key,
    ip_whitelist,
)
from tts.helpers.functions import analyze_sentiment
from tts.models.sentiment import SentimentResponse

sentiment_bp = Blueprint("sentiment", __name__)
proxy_sentiment_bp = Blueprint("proxy_sentiment", __name__)


def process_sentiment_analysis(data) -> SentimentResponse:
    """Helper function to process sentiment analysis."""
    message = data.get("text")
    sentiment_type = data.get("sentiment_type")

    sentiment_result = analyze_sentiment(
        message=message,
        sentiment_type=sentiment_type,
    )
    return SentimentResponse(
        text=message,
        sentiment_result=sentiment_result,
    )


@sentiment_bp.route("/api/v1/sentiment-analysis", methods=["POST"])
@require_api_key
@handle_exceptions
def sentiment_analysis() -> jsonify:
    """Sentiment analysis API endpoint."""
    data = request.get_json()
    response = process_sentiment_analysis(data)
    return response.model_dump_json()


@proxy_sentiment_bp.route(
    "/api/v1/proxy-sentiment-analysis", methods=["POST", "OPTIONS"]
)
@handle_exceptions
@ip_whitelist
def proxy_sentiment_analysis() -> jsonify:
    """Proxy for the sentiment analysis API endpoint."""
    if request.method == "OPTIONS":
        return "", 204

    api_key = request.headers.get("Authorization")
    if (
        api_key != EnvironmentVariables.API_KEY
        and not current_app.config["TESTING"]
    ):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    response = process_sentiment_analysis(data)
    return response.model_dump_json()
