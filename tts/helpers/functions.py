import hmac
import hashlib
import time
import functools
from typing import Optional

from langdetect import detect, LangDetectException

from tts.extensions import config_tts
from tts.models.sentiment import SentimentRequest


def load_models():
    """Load the sentiment analysis models."""
    from transformers import (
        pipeline,
        TFDistilBertForSequenceClassification,
        DistilBertTokenizer,
    )
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    vader_analyzer_ = SentimentIntensityAnalyzer()

    model_name = (
        "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # noqa
    )
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = TFDistilBertForSequenceClassification.from_pretrained(model_name)
    transformer_sentiment_ = pipeline(
        "sentiment-analysis", model=model, tokenizer=tokenizer
    )

    return vader_analyzer_, transformer_sentiment_


vader_analyzer, transformer_sentiment = load_models()


def prepare_sentiment_analysis(
    sentiment_type_from_request: Optional[str] = None,
) -> tuple:
    """Prepare the sentiment analysis based on the sentiment type."""

    match sentiment_type_from_request or config_tts.project.sentiment_type:
        case "vader":
            return vader_analyzer, None
        case "transformer":
            return None, transformer_sentiment
        case "all":
            return vader_analyzer, transformer_sentiment
        case _:
            raise ValueError("Invalid sentiment type.")


@functools.lru_cache(maxsize=5)
def get_sentiment_scores(sentiment_type_, message, sentiment_analysis_result):
    """Get sentiment scores based on the sentiment type."""
    if sentiment_type_ == "vader":
        sia, _ = sentiment_analysis_result
        return None, sia.polarity_scores(message)
    elif sentiment_type_ == "transformer":
        _, transformer_sentiment_ = sentiment_analysis_result
        transformer_sentiment_scores = transformer_sentiment_(message)
        return transformer_sentiment_scores[0], None
    else:
        sia, transformer_sentiment_ = sentiment_analysis_result
        vader_sentiment_scores = sia.polarity_scores(message)
        transformer_sentiment_scores = transformer_sentiment_(message)
        return transformer_sentiment_scores[0], vader_sentiment_scores


def determine_sentiment_all_models(
    transformers_scores: Optional[dict], vader_scores: Optional[dict]
):
    """Determine if the text is genuinely negative based on both sentiment models.

    :param transformers_scores: (dict) The scores from the transformer model.
    :param vader_scores: (dict) The scores from the VADER model.
    :returns: (str) Final sentiment classification.
    """

    if not transformers_scores and not vader_scores:
        raise ValueError("No sentiment scores provided.")

    if not transformers_scores:
        return determine_sentiment_vader(vader_scores)
    if not vader_scores:
        return determine_sentiment_transformer(transformers_scores)

    transformer_score = transformers_scores.get("score")
    vader_score = vader_scores.get("compound")

    if transformer_score < 0.5 and vader_score < 0:
        return "definitely negative"
    elif transformer_score >= 0.5 and vader_score < 0:
        return "possibly negative"
    elif transformer_score == 0.5 and vader_score == 0:
        return "neutral"
    elif transformer_score >= 0.5 or vader_score >= 0:
        return "definitely not negative"
    return "possibly not negative"


def determine_sentiment_vader(vader_scores: dict):
    """Determine if the text is genuinely negative based on the VADER sentiment model.

    :param vader_scores: (dict) The scores from the VADER model.
    :returns: (str) Final sentiment classification.
    """
    vader_score = vader_scores["compound"]

    if vader_score < 0:
        return "negative"
    return "not negative"


def determine_sentiment_transformer(transformers_scores: dict):
    """Determine if the text is genuinely negative based on the transformer sentiment model.

    :param transformers_scores: (dict) The scores from the transformer model.
    :returns: (str) Final sentiment classification.
    """
    transformer_score = transformers_scores["score"]

    if transformer_score < 0.5:
        return "negative"
    return "not negative"


def analyze_sentiment(
    message: str,
    sentiment_type: Optional[str] = None,
) -> str:
    """Sends a request for sentiment analysis."""
    data = {
        "sentiment_type": sentiment_type or config_tts.project.sentiment_type,
        "text": message,
    }
    sentiment_request = SentimentRequest(**data)

    sentiment_analysis_result = prepare_sentiment_analysis(
        sentiment_request.sentiment_type
    )
    transformer_sentiment_score, vader_sentiment_scores = get_sentiment_scores(
        sentiment_type_=sentiment_request.sentiment_type,
        message=sentiment_request.text,
        sentiment_analysis_result=sentiment_analysis_result,
    )
    sentiment_result = determine_sentiment_all_models(
        transformers_scores=transformer_sentiment_score,
        vader_scores=vader_sentiment_scores,
    )
    return sentiment_result


def is_negative_sentiment(sentiment_result: str) -> bool:
    """Checks if the sentiment is negative."""
    return "negative" in sentiment_result and "not" not in sentiment_result


def is_english(text: str) -> bool:
    """Checks if the given text is in English."""
    try:
        language = detect(text)
        return language == "en"
    except (LangDetectException, Exception) as e:
        if isinstance(e, LangDetectException):
            return False
        return True


def verify_slack_app_signature(signing_secret: str, request_: any) -> bool:
    """Verify the Slack app signature."""

    timestamp = request_.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request_.headers.get("X-Slack-Signature")

    if not timestamp or not slack_signature:
        return False

    if abs(time.time() - int(timestamp)) > 60 * 2:
        return False

    request_body = request_.get_data(as_text=True)
    sig_basestring = f"v0:{timestamp}:{request_body}"

    calculated_signature = hmac.new(
        signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()

    calculated_signature = f"v0={calculated_signature}"
    if hmac.compare_digest(calculated_signature, slack_signature):
        return True
    else:
        return False
