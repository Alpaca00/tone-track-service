import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from tts.controllers.slack.http.slack_controller import Routes
from tts.controllers.slack.http.constants import (
    RESPONSE_ACTION_CLEAR,
    INVALID_FORM_MESSAGE,
)
from tts.models.slack_application import modal_view_callback_id


@pytest.fixture
def interaction_payload():
    """Fixture providing a sample payload from Slack interaction."""
    return {
        "type": "view_submission",
        "team": {"id": "T123", "domain": "test_team"},
        "user": {
            "id": "U123",
            "username": "test_user",
            "name": "Test User",
            "team_id": "T123",
        },
        "api_app_id": "A123",
        "trigger_id": "trigger123",
        "view": {
            "callback_id": modal_view_callback_id,
            "state": {
                "values": {
                    "block_id": {
                        "action_id": {
                            "type": "plain_text_input",
                            "value": "sample input",
                        }
                    }
                }
            },
        },
    }


@patch(
    "tts.controllers.slack.http.slack_controller.request", new_callable=MagicMock
)
@patch(
    "tts.controllers.slack.http.slack_controller.client_slack.chat_postMessage",
    new_callable=AsyncMock,
)
def test_slack_app_interaction_invalid_callback_id(
    mock_chat_postMessage, mock_request, client, interaction_payload  # noqa
):
    """Test handling of Slack interaction with an invalid callback_id."""
    interaction_payload["view"]["callback_id"] = "invalid_callback_id"
    mock_request.form.get.return_value = json.dumps(interaction_payload)

    response = client.post(Routes.INTERACTIONS)

    assert response.status_code == 462
    assert response.get_json() == RESPONSE_ACTION_CLEAR

    mock_chat_postMessage.assert_called_once_with(
        channel="U123", text=INVALID_FORM_MESSAGE
    )
