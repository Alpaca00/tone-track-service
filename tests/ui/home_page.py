from typing import Self
from playwright.sync_api import Page, expect

from tests.ui.locators import HomePageLocators


class Home:
    """Page object for the ToneTrack home page."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, base_url: str) -> Self:
        """Navigate to the ToneTrack home page."""
        self.page.goto(base_url)
        expect(
            self.page.locator(HomePageLocators.INPUT_TEXT_FIELD)
        ).to_be_visible()
        return self

    def fill_sentiment_analysis_input(self, text: str) -> Self:
        """Fill the sentiment analysis input field."""
        self.page.fill(HomePageLocators.INPUT_TEXT_FIELD, text)
        return self

    def submit_sentiment_analysis(self) -> Self:
        """Click the sentiment analysis submit button."""
        self.page.click(HomePageLocators.SUBMIT_BUTTON)
        return self

    def get_primary_heading_text(self) -> Page.locator:
        """Retrieve the text of the primary heading."""
        return self.page.locator(HomePageLocators.PRIMARY_HEADING)

    def verify_sentiment_analysis_result(self, expected_result: str):
        """Verify the sentiment analysis result."""
        expect(self.get_primary_heading_text()).to_contain_text(expected_result)
