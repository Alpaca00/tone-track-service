from flask import Blueprint, request, jsonify

from tts.helpers.decorators import handle_exceptions, require_api_key
from tts.helpers.functions import (
    determine_sentiment_all_models,
    prepare_sentiment_analysis,
    get_sentiment_scores,
)
from tts.models.sentiment import SentimentRequest, SentimentResponse


sentiment_bp = Blueprint("sentiment", __name__)


@sentiment_bp.route("/api/v1/sentiment-analysis", methods=["POST"])
@require_api_key
@handle_exceptions
def sentiment_analysis() -> jsonify:
    """Sentiment analysis API endpoint."""

    data = request.get_json()
    sentiment_request = SentimentRequest(**data)

    sentiment_analysis_result = prepare_sentiment_analysis(
        sentiment_request.text, sentiment_request.sentiment_type
    )
    transformer_sentiment_score, vader_sentiment_scores = get_sentiment_scores(
        sentiment_request.sentiment_type,
        sentiment_request.text,
        sentiment_analysis_result,
    )
    sentiment_result = determine_sentiment_all_models(
        transformers_scores=transformer_sentiment_score,
        vader_scores=vader_sentiment_scores,
    )
    response = SentimentResponse(
        text=sentiment_request.text,
        sentiment_result=sentiment_result,
    )
    return response.model_dump_json()
