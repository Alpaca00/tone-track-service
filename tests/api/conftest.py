import os

import pytest

from tts.helpers.common import Config
from tests.api.client import APIClient


@pytest.fixture(scope="function")
def config() -> Config:
    """Fixture for the configuration object."""

    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
    config_path = os.path.join(project_root, "config.ini")

    return Config(file_path=config_path)


@pytest.fixture(scope="function")
def client(config) -> APIClient:
    """Fixture for the API client."""

    base_url = config.resources.external_server_url

    return APIClient(base_url=base_url)
