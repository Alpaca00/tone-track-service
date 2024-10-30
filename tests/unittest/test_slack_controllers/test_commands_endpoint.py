from unittest.mock import patch
import pytest

from tts.controllers.slack.http.constants import COMMANDS, RESPONSE_ACTION_CLEAR
from tts.controllers.slack.http.slack_controller import Routes


@pytest.fixture
def command_data():
    return {
        "user_id": "U123",
        "team_id": "T123",
        "team_domain": "test-domain",
        "channel_id": "C123",
        "channel_name": "general",
    }


@patch("tts.controllers.slack.http.slack_controller.request")
@patch("tts.controllers.slack.http.slack_controller.open_modal")
@patch(
    "tts.controllers.slack.http.slack_controller.client_redis.store_user_data_with_ttl"
)
def test_slack_app_commands_add(
    mock_store_user_data, mock_open_modal, mock_request, client, command_data
):
    """Test handling of the add Slack command."""
    command_data["command"] = COMMANDS["add"]
    mock_request.form = command_data
    mock_open_modal.return_value = "Modal opened"

    response = client.post(Routes.COMMANDS)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Modal opened"

    mock_store_user_data.assert_called_once_with(
        user_id="U123",
        team_id="T123",
        team_domain="test-domain",
        channel_id="C123",
        channel_name="general",
    )
    mock_open_modal.assert_called_once_with(command_data)


@patch("tts.controllers.slack.http.slack_controller.request")
@patch("tts.controllers.slack.http.slack_controller.read_message_for_channel")
def test_slack_app_commands_read(
    mock_read_message, mock_request, client, command_data
):
    """Test handling of the read Slack command."""
    command_data["command"] = COMMANDS["read"]
    mock_request.form = command_data
    mock_read_message.return_value = "Message read"

    response = client.post(Routes.COMMANDS)

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "Message read"
    mock_read_message.assert_called_once_with(command_data)


@patch("tts.controllers.slack.http.slack_controller.request")
def test_slack_app_commands_invalid_command(mock_request, client, command_data):
    """Test handling of an invalid Slack command."""
    command_data["command"] = "/invalid_command"
    mock_request.form = command_data

    response = client.post(Routes.COMMANDS)

    assert response.status_code == 461
    assert response.get_json() == RESPONSE_ACTION_CLEAR
