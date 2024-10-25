import json

from flask import Blueprint, request, jsonify, redirect

# from tts.controllers.slack.http.auth import validate_request_signature
from tts.controllers.slack.http.constants import (
    COMMANDS,
    INVALID_FORM_MESSAGE,
    RESPONSE_ACTION_CLEAR,
)
from tts.controllers.slack.http.event_handlers import handle_event_callback
from tts.controllers.slack.http.messages import read_message_for_channel
from tts.controllers.slack.http.modals import handle_modal_submission, open_modal
from tts.extensions import client_redis, client_slack
from tts.helpers.decorators import handle_slack_exceptions

from tts.models.slack_application import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
    SlackInteractionModalResponse,
    modal_view_callback_id,
)
from tts.models.slack_application.interaction.add import RedisValuesValidated

slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)
slack_commands = Blueprint("slack_commands", __name__)
slack_interactions = Blueprint("slack_interactions", __name__)


class Routes:
    """Routes for the Slack app."""

    EVENTS = "/api/v1/slack/events"
    VERIFICATION = "/api/v1/slack/verification"
    COMMANDS = "/api/v1/slack/commands"
    INTERACTIONS = "/api/v1/slack/interactions"


@slack_events.route(Routes.EVENTS, methods=["POST"])
@handle_slack_exceptions
def slack_app_events():
    """The endpoint for Slack events orchestration."""
    data = request.get_json()
    event_type = data.get("type")

    if event_type == "url_verification":
        return redirect(Routes.VERIFICATION, code=307)
    elif event_type == "event_callback":
        # validate_request_signature(request)
        return handle_event_callback(data)

    return jsonify(RESPONSE_ACTION_CLEAR), 460


@slack_verification.route(Routes.VERIFICATION, methods=["POST"])
@handle_slack_exceptions
def slack_app_verification():
    """The endpoint for Slack URL verification."""
    data = request.get_json()
    validate_req = SlackVerificationRequest(**data)
    response = SlackVerificationChallengeResponse(
        challenge=validate_req.challenge
    )
    return response.model_dump_json(), 200


@slack_commands.route(Routes.COMMANDS, methods=["POST"])
@handle_slack_exceptions
def slack_app_commands():
    """The endpoint for Slack commands."""
    # validate_request_signature(request)

    data = request.form
    command = data.get("command")

    if command == COMMANDS["add"]:
        redis_values = RedisValuesValidated(**data)

        client_redis.store_user_data_with_ttl(
            user_id=redis_values.user_id,
            team_id=redis_values.team_id,
            team_domain=redis_values.team_domain,
            channel_id=redis_values.channel_id,
            channel_name=redis_values.channel_name,
        )
        return open_modal(data)
    elif command == COMMANDS["read"]:
        return read_message_for_channel(data)

    return jsonify(RESPONSE_ACTION_CLEAR), 461


@slack_interactions.route(Routes.INTERACTIONS, methods=["POST"])
@handle_slack_exceptions
def slack_app_interaction():
    """Handle interactions from Slack modal."""
    # validate_request_signature(request)
    payload = request.form.get("payload")

    payload_dict = json.loads(payload)
    validate_req = SlackInteractionModalResponse(**payload_dict)

    if validate_req.view.callback_id == modal_view_callback_id:
        return handle_modal_submission(client_slack, validate_req)
    else:
        client_slack.chat_postMessage(
            channel=validate_req.user.id, text=INVALID_FORM_MESSAGE
        )
        return jsonify(RESPONSE_ACTION_CLEAR), 462
