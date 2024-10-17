from flask import Blueprint, request, jsonify
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import (
    pipeline,
    TFDistilBertForSequenceClassification,
    DistilBertTokenizer,
)

from tts.helpers.decorators import handle_exceptions, require_api_key
from tts.helpers.functions import determine_sentiment
from tts.models.sentiment import SentimentRequest, SentimentResponse


sentiment_bp = Blueprint("sentiment", __name__)
sia = SentimentIntensityAnalyzer()
model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = TFDistilBertForSequenceClassification.from_pretrained(model_name)
transformer_sentiment = pipeline(
    "sentiment-analysis", model=model, tokenizer=tokenizer
)


@sentiment_bp.route("/api/v1/sentiment-analysis", methods=["POST"])
@require_api_key
@handle_exceptions
def sentiment_analysis() -> jsonify:
    """Sentiment analysis API.

    :returns: JSON object with the sentiment scores and overall sentiment.
    """
    data = request.get_json()
    sentiment_request = SentimentRequest(**data)

    vader_sentiment_scores = sia.polarity_scores(sentiment_request.text)
    transformer_sentiment_scores = transformer_sentiment(sentiment_request.text)
    transformer_sentiment_score = transformer_sentiment_scores[0]

    params = {
        "text": sentiment_request.text,
        "transformer_sentiment_scores": transformer_sentiment_score,
        "vader_sentiment_scores": vader_sentiment_scores,
    }
    if sentiment_request.process_text:
        sentiment_result = determine_sentiment(
            params["transformer_sentiment_scores"],
            params["vader_sentiment_scores"],
        )
        response = SentimentResponse(
            **params,
            sentiment_result=sentiment_result,
        )
    else:
        response = SentimentResponse(**params)
    return response.model_dump_json()
