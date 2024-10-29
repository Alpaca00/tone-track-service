import warnings

import pytest
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright


class AccessibilityClient:
    """Client class to perform accessibility tests on a web page."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.axe = Axe()

    def run_test(self):
        """Run the accessibility test and return results."""
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.base_url)
            results = self.axe.run(page)
            browser.close()
        return results


class AccessibilityValidator:
    """Validator class for checking accessibility violations."""

    @staticmethod
    def soft_check_violations(results):
        """Check for accessibility violations."""
        if results.violations_count > 0:
            print(f"Found {results.violations_count} accessibility violations.")
        else:
            print(f"No accessibility violations found on '{results.base_url}'.")
        return results.violations_count

    @staticmethod
    def soft_check_critical_violations(results):
        """Check for critical accessibility violations."""
        critical_violations = [
            violation
            for violation in results.response["violations"]
            if violation["impact"] == "critical"
        ]

        if critical_violations:
            print(
                f"Found {len(critical_violations)} critical accessibility violations:"
            )
            for violation in critical_violations:
                print(f":: {violation['id']}: {violation['description']}")
                for node in violation["nodes"]:
                    print(f" :: Element: {node['html']}")
                    print(f" ::   Target: {node['target']}")
        return critical_violations

    @staticmethod
    def hard_check_image_alt(results):
        """Check for <img> elements missing alternate text (hard check)."""
        assert all(
            violation["id"] != "image-alt"
            for violation in results.response["violations"]
        ), "Critical: Ensure all <img> elements have alternate text."

    @staticmethod
    def soft_check_image_alt(results):
        """Check for <img> elements missing alternate text (soft check)."""
        missing_alt_images = [
            violation
            for violation in results.response["violations"]
            if violation["id"] == "image-alt"
        ]

        if missing_alt_images:
            warnings.warn(
                "Soft Warning: Some <img> elements are missing alternate text."
            )
            for violation in missing_alt_images:
                for node in violation["nodes"]:
                    print(f":: Element: {node['html']}")
                    print(f"::   Target: {node['target']}")

    @staticmethod
    def hard_check_meta_viewport(results):
        """Check viewport meta tag (hard check)."""
        assert not any(
            violation["id"] == "meta-viewport"
            for violation in results.response["violations"]
        ), "Critical: Ensure <meta name='viewport'> does not disable text scaling and zooming."

    @staticmethod
    def soft_check_meta_viewport(results):
        """Check viewport meta tag (soft check)."""
        if any(
            violation["id"] == "meta-viewport"
            for violation in results.response["violations"]
        ):
            warnings.warn(
                "Soft Warning: <meta name='viewport'> may disable text scaling and zooming."
            )


@pytest.fixture(scope="module")
def ready_result():
    """Return the accessibility test results."""
    client = AccessibilityClient("https://tone-track.uno")
    results = client.run_test()
    return results


XFAIL_CRITICAL_REASON = """
[{'description': 'Ensures <img> elements have alternate text or a role of none or presentation', 'help': 'Images must have alternate text', 'helpUrl': 'https://dequeuniversity.com/rules/axe/4.4/image-alt?application=axeAPI', 'id': 'image-alt', ...}, {'description': 'Ensures <meta name="viewport"> does not disable text scaling and zooming', 'help': 'Zooming and scaling should not be disabled', 'helpUrl': 'https://dequeuniversity.com/rules/axe/4.4/meta-viewport?application=axeAPI', 'id': 'meta-viewport', ...}]
"""

XFAIL_IMAGE_ALT_REASON = """
:: Element: <img src="/static/images/flags/US.png">
::   Target: ['img[src$="US.png"]']
:: Element: <img src="/static/images/flags/GB.png">
::   Target: ['img[src$="GB.png"]']
"""

META_VIEWPORT_REASON = """
Some <img> elements are missing alternate text.
 <meta name='viewport'> may disable text scaling and zooming.
"""


class TestAccessibilityViolations:
    """Test the accessibility violations on the home page."""

    @pytest.mark.xfail(
        reason="Expected 7 accessibility violations.",
    )
    def test_violation_count(self, ready_result):
        """Test the number of accessibility violations."""
        violation_count = AccessibilityValidator.soft_check_violations(
            ready_result
        )
        assert (
            violation_count == 0
        ), f"Expected 0 accessibility violations, found {violation_count}."

    @pytest.mark.xfail(
        reason=XFAIL_CRITICAL_REASON,
    )
    def test_critical_violations(self, ready_result):
        """Test the critical accessibility violations."""
        critical_violations = (
            AccessibilityValidator.soft_check_critical_violations(ready_result)
        )
        assert not critical_violations, "No critical violations found."

    @pytest.mark.xfail(reason=XFAIL_IMAGE_ALT_REASON)
    def test_image_alt(self, ready_result):
        """Test for missing alternate text on <img> elements."""
        image_alt = AccessibilityValidator()

        image_alt.soft_check_image_alt(ready_result)
        image_alt.hard_check_image_alt(ready_result)

    @pytest.mark.xfail(reason=META_VIEWPORT_REASON)
    def test_meta_viewport(self, ready_result):
        """Test the viewport meta tag."""
        meta_viewport = AccessibilityValidator()

        meta_viewport.soft_check_meta_viewport(ready_result)
        meta_viewport.hard_check_meta_viewport(ready_result)
