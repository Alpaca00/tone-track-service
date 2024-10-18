from flask import Blueprint, request, jsonify

from tts.helpers.decorators import handle_exceptions, require_api_key
from tts.helpers.functions import analyze_sentiment
from tts.models.sentiment import SentimentResponse


sentiment_bp = Blueprint("sentiment", __name__)


@sentiment_bp.route("/api/v1/sentiment-analysis", methods=["POST"])
@require_api_key
@handle_exceptions
def sentiment_analysis() -> jsonify:
    """Sentiment analysis API endpoint."""

    data = request.get_json()
    message = data.get("text")
    sentiment_type = data.get("sentiment_type")

    sentiment_result = analyze_sentiment(
        message=message,
        sentiment_type=sentiment_type,
    )
    response = SentimentResponse(
        text=message,
        sentiment_result=sentiment_result,
    )
    return response.model_dump_json()
