import pytest

from tts.helpers.functions import determine_sentiment_all_models


@pytest.mark.parametrize(
    "transformers_scores, vader_scores, expected_result",
    [
        ({"score": 0.8}, {"compound": -0.1}, "possibly negative"),
        ({"score": 0.9}, {"compound": 0.0}, "definitely not negative"),
        ({"score": 0.5}, {"compound": 0.0}, "neutral"),
        ({"score": 0.2}, {"compound": -0.5}, "definitely negative"),
    ],
    ids=[
        "possibly negative",
        "definitely not negative",
        "neutral",
        "definitely negative",
    ],
)
@pytest.mark.determine_sentiment_unittest
def test_determine_sentiment(transformers_scores, vader_scores, expected_result):
    """Test the determine_sentiment function."""
    assert (
        determine_sentiment_all_models(transformers_scores, vader_scores)
        == expected_result
    )
