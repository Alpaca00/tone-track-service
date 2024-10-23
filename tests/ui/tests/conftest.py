import random

import pytest
from playwright.sync_api import Page, sync_playwright

from tests.ui.home_page import Home
from tests.ui.navbar_page import Navbar
from tts.extensions import config_tts


def pytest_addoption(parser):  # noqa
    """Add an option to the pytest command."""
    parser.addoption(
        "--env",
        action="store",
        default="external",
        help="Which resource to use for the tests, e.g. external, internal",
    )
    parser.addoption(
        "--headless",
        action="store",
        default=True,
        help="Run the browser in headless mode",
    )
    parser.addoption(
        "--slow-mo",
        action="store",
        default=50,
        help="Slow down the browser operations",
    )
    parser.addoption(
        "--devtools",
        action="store",
        default=False,
        help="Run the browser with devtools",
    )
    parser.addoption(
        "--browser-type",
        action="store",
        default="chromium",
        help="Which browser to use for the tests, e.g. chromium, firefox",
    )
    parser.addoption(
        "--timeout",
        action="store",
        default=10000,
        help="Default timeout for Playwright operations",
    )
    parser.addoption(
        "--viewport",
        action="store",
        default="1920x1080",
        help="Default viewport for Playwright operations",
    )
    parser.addoption(
        "--viewport-random",
        action="store_true",
        default=True,
        help="Randomize the viewport size for Playwright operations",
    )


@pytest.fixture(scope="session", autouse=True)
def configuration(request):
    """Fixture to get the configuration options from the command line."""
    cli_options = {
        "env": request.config.getoption("--env"),
        "headless": request.config.getoption("--headless"),
        "slowmo": request.config.getoption("--slowmo"),
        "devtools": request.config.getoption("--devtools"),
        "browser": request.config.getoption("--browser"),
        "timeout": request.config.getoption("--timeout"),
        "viewport": request.config.getoption("--viewport"),
        "viewport-random": request.config.getoption("--viewport-random"),
    }
    return cli_options


@pytest.fixture(scope="session")
def base_url(configuration):
    """Fixture to get the base URL based on the --env option."""
    if configuration["env"] == "external":
        return config_tts.resources.external_server_url
    elif configuration["env"] == "internal":
        return config_tts.resources.internal_server_url
    else:
        raise ValueError("Please provide a valid environment")


def log_request(request):
    """Logs to stdout the request method and URL."""
    print(f"Request: {request.method} {request.url}")


def log_response(response):
    """Logs to stdout the response status and URL."""
    print(f"Response: {response.status} {response.url}")


@pytest.fixture(scope="session", autouse=True)
def setup_session(configuration):
    """Fixture to configure browser settings before the session starts and clean up after the session ends."""

    viewport_list = [
        (1920, 1080),
        (1366, 768),
        (1280, 800),
        (1024, 768),
        (800, 600),
    ]

    def get_viewport_size(config):
        """Return the viewport size based on the configuration."""
        if config["viewport-random"]:
            return random.choice(viewport_list)
        else:
            try:
                width, height = map(int, config["viewport"].split("x"))
                return width, height
            except ValueError:
                raise ValueError("Invalid viewport format.")

    viewport_width, viewport_height = get_viewport_size(configuration)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=configuration["headless"],
            slow_mo=configuration["slowmo"],
            devtools=configuration["devtools"],
        )
        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        context.on("request", log_request)
        context.on("response", log_response)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(setup_session: sync_playwright, configuration) -> Page:
    """Fixture to create a new page object with default settings."""
    page = setup_session.new_page()
    page.set_default_navigation_timeout(configuration["timeout"])
    page.set_default_timeout(configuration["timeout"])
    return page


@pytest.fixture(scope="function")
def home(page) -> Home:
    """Fixture to return the Home page object."""
    return Home(page)


@pytest.fixture(scope="function")
def navbar(page) -> Navbar:
    """Fixture to return the Navbar page object."""
    return Navbar(page)
