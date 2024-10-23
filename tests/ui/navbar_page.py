from playwright.sync_api import Page, expect

from tests.ui.locators import NavbarLocators


class Navbar:
    """Page object for the ToneTrack navbar."""

    def __init__(self, page: Page):
        self.page = page

    def verify_github_and_email_icons(self):
        """Verify that the GitHub and Email icons are visible in the navbar."""
        expect(self.page.locator(NavbarLocators.GITHUB_ICON)).to_be_visible()
        expect(self.page.locator(NavbarLocators.EMAIL_ICON)).to_be_visible()
