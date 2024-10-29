from unittest.mock import patch, AsyncMock, MagicMock

from tts.controllers.slack.http.constants import RESPONSE_ACTION_CLEAR
from tts.controllers.slack.http.slack_controller import Routes


@patch(
    "tts.controllers.slack.http.slack_controller.request", new_callable=MagicMock
)
@patch(
    "tts.controllers.slack.http.slack_controller.handle_event_callback",
    new_callable=AsyncMock,
)
def test_url_verification_event(mock_handle_event_callback, mock_request, client):
    """Test handling of url_verification event type."""
    mock_request.get_json.return_value = {
        "type": "url_verification",
        "challenge": "1234567890",
        "token": "0987654321",
    }
    response = client.post(Routes.EVENTS)

    assert (
        response.status_code == 307
    ), f"Expected 307, but got {response.status_code}"
    assert Routes.VERIFICATION in response.location
    mock_handle_event_callback.assert_not_called()


@patch(
    "tts.controllers.slack.http.slack_controller.request", new_callable=MagicMock
)
@patch(
    "tts.controllers.slack.http.slack_controller.handle_event_callback",
    new_callable=MagicMock,
)
def test_event_callback(mock_handle_event_callback, mock_request, client):
    """Test handling of event_callback event type."""
    mock_request.get_json.return_value = {"type": "event_callback"}
    mock_handle_event_callback.return_value = RESPONSE_ACTION_CLEAR

    response = client.post(Routes.EVENTS)

    assert response.status_code == 200
    assert response.get_json() == RESPONSE_ACTION_CLEAR
    mock_handle_event_callback.assert_called_once_with({"type": "event_callback"})


@patch(
    "tts.controllers.slack.http.slack_controller.request", new_callable=MagicMock
)
def test_unknown_event_type(mock_request, client):
    """Test handling of unknown event type."""
    mock_request.get_json.return_value = {"type": "unknown_event"}

    response = client.post(Routes.EVENTS)

    assert response.status_code == 460
    assert response.get_json() == RESPONSE_ACTION_CLEAR
