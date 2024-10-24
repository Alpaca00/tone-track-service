import pytest


@pytest.mark.website
class TestWebsite:
    """Tests for the ToneTrack website."""

    @pytest.mark.parametrize(
        "input_text, expected_result",
        [
            ("I love Tone Track!", "not negative"),
            ("I hate Tone Track!", "negative"),
        ],
        ids=["positive", "negative"],
    )
    def test_functionality_sentiment_analysis(
        self, home, base_url, input_text, expected_result
    ):
        """Test the functionality of the sentiment analysis form."""
        home.navigate(base_url)
        home.fill_sentiment_analysis_input(input_text)
        home.submit_sentiment_analysis()
        home.verify_sentiment_analysis_result(expected_result)

    def test_navbar_visibility(self, home, navbar, base_url):
        """Test that the navbar is visible on the home page."""
        home.navigate(base_url)
        navbar.verify_github_and_email_icons()
