import configparser
import functools
from typing import final, Optional


class Config:
    def __init__(self, file_path: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def __getattr__(self, section):
        """Get a section as an attribute."""
        if section in self.config:
            return ConfigSection(self.config[section])
        raise AttributeError(f"Section '{section}' not found in configuration.")


class ConfigSection:
    def __init__(self, section):
        self.section = section

    def __getattr__(self, key):
        """Get a key as an attribute."""
        if key in self.section:
            return self.section[key]
        raise AttributeError(f"Key '{key}' not found in section.")


config = Config()
sentiment_type_from_config: final = config.project.sentiment_type


@functools.lru_cache(maxsize=5)
def prepare_sentiment_analysis(
    message: str, sentiment_type_from_request: str
) -> tuple:  # noqa  # message parameter is not used due to caching
    """Prepare the sentiment analysis models."""

    def transform_model():
        """Prepare the transformer sentiment analysis pipeline."""
        from transformers import (
            pipeline,
            TFDistilBertForSequenceClassification,
            DistilBertTokenizer,
        )

        model_name = (
            "distilbert/distilbert-base-uncased-finetuned-sst-2-english"  # noqa
        )
        tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        model = TFDistilBertForSequenceClassification.from_pretrained(model_name)
        transformer_sentiment = pipeline(
            "sentiment-analysis", model=model, tokenizer=tokenizer
        )
        return transformer_sentiment

    def vader_model():
        """Prepare the VADER sentiment analysis model."""
        from nltk.sentiment.vader import SentimentIntensityAnalyzer

        return SentimentIntensityAnalyzer()

    match sentiment_type_from_request or sentiment_type_from_config:
        case "vader":
            return vader_model(), None
        case "transformer":
            return None, transform_model()
        case "all":
            return vader_model(), transform_model()
        case _:
            raise ValueError("Invalid sentiment type.")


def get_sentiment_scores(sentiment_type_, message, sentiment_analysis_result):
    """Get sentiment scores based on the sentiment type."""
    if sentiment_type_ == "vader":
        sia, _ = sentiment_analysis_result
        return None, sia.polarity_scores(message)
    elif sentiment_type_ == "transformer":
        _, transformer_sentiment = sentiment_analysis_result
        transformer_sentiment_scores = transformer_sentiment(message)
        return transformer_sentiment_scores[0], None
    else:
        sia, transformer_sentiment = sentiment_analysis_result
        vader_sentiment_scores = sia.polarity_scores(message)
        transformer_sentiment_scores = transformer_sentiment(message)
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
