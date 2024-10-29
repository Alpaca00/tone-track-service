import pytest
from unittest.mock import mock_open, patch

from tts.helpers.common import Config

mock_config_data = """
[resources]
host = localhost
port = 5432

[project]
key = my_secret_key
"""


@pytest.fixture
def config():
    """Fixture creating Config object with mock data."""
    with patch("builtins.open", mock_open(read_data=mock_config_data)):
        return Config("test_config.ini")


def test_get_existing_section_and_key(config):
    """Test getting an existing section and key."""
    assert config.resources.host == "localhost"
    assert config.resources.port == "5432"
    assert config.project.key == "my_secret_key"


def test_missing_section(config):
    """Test handling missing section."""
    with pytest.raises(
        AttributeError,
        match="Section 'non_existent_section' not found in configuration.",
    ):
        _ = config.non_existent_section


def test_missing_key_in_section(config):
    """Test handling missing key in section."""
    with pytest.raises(
        AttributeError, match="Key 'non_existent_key' not found in section."
    ):
        _ = config.project.non_existent_key


def test_empty_config_file():
    """Test handling an empty configuration file."""
    with patch("builtins.open", mock_open(read_data="")):
        config = Config("test_config.ini")
        with pytest.raises(
            AttributeError, match="Section 'project' not found in configuration."
        ):
            _ = config.project
