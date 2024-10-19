import json
from typing import final

from flask import Blueprint, request, jsonify, redirect
from pydantic import ValidationError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from tts.extensions import env_variables
from tts.helpers.constants import EnvironmentVariables
from tts.helpers.decorators import handle_exceptions
from tts.helpers.functions import (
    analyze_sentiment,
    verify_slack_app_signature,
    is_negative_sentiment,
)
from tts.models.db.base import initialize_database, DatabaseManager
from tts.models.slack_application import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
    SlackInteractionModalResponse,
    modal_view_callback_id,
    modal_view,
)

slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)
slack_commands = Blueprint("slack_commands", __name__)
slack_interactions = Blueprint("slack_interactions", __name__)


SIGNATURE_VERIFICATION_ERROR: final = {"error": "Signature verification failed."}
UNSUPPORTED_EVENT_TYPE: final = {"message": "Unsupported event type."}
VALIDATION_ERROR_MESSAGE: final = "Validation error occurred."
INVALID_FORM_MESSAGE: final = "Invalid form fields provided."

COMMANDS: final = {
    "add": "/tt-add-workspace",  # Add a workspace and sentiment analysis message
    "info": "/tt-info-workspace",  # Get information about a workspace
    "update": "/tt-update-workspace",  # Update a workspace and sentiment analysis message
}


@slack_events.route("/api/v1/slack/events", methods=["POST"])
@handle_exceptions
def slack_app_events():
    """The endpoint for Slack events orchestration."""
    if not verify_signature(request):
        return jsonify(SIGNATURE_VERIFICATION_ERROR), 400

    data = request.get_json()
    event_type = data.get("type")

    if event_type == "url_verification":
        return redirect("/api/v1/slack/verification", code=307)
    elif event_type == "event_callback":
        return handle_event_callback(data)

    return jsonify(UNSUPPORTED_EVENT_TYPE), 400


@slack_verification.route("/api/v1/slack/verification", methods=["POST"])
@handle_exceptions
def slack_app_verification():
    """The endpoint for Slack URL verification."""
    data = request.get_json()
    verification_request = SlackVerificationRequest(**data)
    response = SlackVerificationChallengeResponse(
        challenge=verification_request.challenge
    )
    return response.model_dump_json(), 200


@slack_commands.route("/api/v1/slack/commands", methods=["POST"])
@handle_exceptions
def slack_app_commands():
    """The endpoint for Slack commands."""
    if not verify_signature(request):
        return jsonify(SIGNATURE_VERIFICATION_ERROR), 400

    data = request.form
    command = data.get("command")

    if command == COMMANDS["add"]:
        return open_modal(data)

    return jsonify({"message": "Unknown command."}), 400


@slack_interactions.route("/api/v1/slack/interactions", methods=["POST"])
@handle_exceptions
def slack_app_interaction():
    """Handle interactions from Slack modal."""
    payload = request.form.get("payload")

    if not payload:
        return jsonify({"message": "No payload provided."}), 400

    client = WebClient(token=env_variables.SLACK_BOT_OAUTH_TOKEN)
    payload_dict = {}
    try:
        payload_dict = json.loads(payload)
        validated_data = SlackInteractionModalResponse(**payload_dict)

        if validated_data.view.callback_id == modal_view_callback_id:
            return handle_modal_submission(client, validated_data)
        else:
            client.chat_postMessage(
                channel=validated_data.user.id, text=INVALID_FORM_MESSAGE
            )
    except ValidationError:
        handle_validation_error(payload_dict, client)
        return jsonify({}), 200
    except SlackApiError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"response_action": "clear"})


def verify_signature(request_) -> bool:
    """Verify Slack request signature."""
    signing_secret = env_variables.SLACK_SIGNING_SECRET
    return verify_slack_app_signature(
        signing_secret=signing_secret, request_=request_
    )


def open_modal(data: dict) -> jsonify:
    """Open a Slack modal for adding a workspace."""
    client = WebClient(token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN)
    trigger_id = data.get("trigger_id")

    try:
        client.views_open(trigger_id=trigger_id, view=modal_view.model_dump())
        return jsonify({}), 200
    except SlackApiError as e:
        return jsonify({"error": str(e)}), 500


def info_workspace(data: dict) -> jsonify:
    """Get information about a workspace."""



    client = WebClient(token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN)
    user_id = data.get("user_id")
    client.chat_postMessage(channel=user_id, text="Workspace information.")

    return jsonify({}), 200

def handle_modal_submission(client: WebClient, validated_data) -> jsonify:
    """Handle the submission of a Slack modal."""
    state_values = validated_data.view.state.values
    workspace_name = state_values["workspace_name_block"]["workspace_name"].value
    workspace_email = state_values["workspace_email_block"][
        "workspace_email"
    ].value
    workspace_message = state_values["message_reply_block"]["message_reply"].value

    initialize_database()
    db_manager = DatabaseManager()
    db_manager.add_workspace(
        name=workspace_name,
        email=workspace_email,
        sentiment_message=workspace_message,
    )

    client.chat_postMessage(
        channel=validated_data.user.id,
        text="Workspace added successfully.",
        mrkdwn=True,
        attachments=[
            {
                "color": "yellow",
                "fields": [
                    {
                        "title": "Workspace Name",
                        "value": workspace_name,
                        "short": False,
                    },
                    {
                        "title": "Workspace Email",
                        "value": workspace_email,
                        "short": False,
                    },
                    {
                        "title": "Sentiment Message",
                        "value": workspace_message,
                        "short": False,
                    },
                ],
            }
        ],
    )

    return jsonify({"response_action": "clear"})


def handle_validation_error(payload_dict, client: WebClient):
    """Handle validation errors."""
    channel_id = payload_dict.get("user").get("id")
    client.chat_postMessage(channel=channel_id, text=VALIDATION_ERROR_MESSAGE)


def handle_event_callback(data: dict) -> jsonify:
    """Handles the event callback from Slack."""
    event = data.get("event")

    if not event:
        return jsonify({"error": "Event not found."}), 400

    message = event.get("text")
    channel = event.get("channel")
    username = event.get("user")
    token = env_variables.SLACK_BOT_OAUTH_TOKEN

    sentiment_result = analyze_sentiment(message=message)
    if is_negative_sentiment(sentiment_result) and token and message:
        message = (
            message[0:30] + " ..."
            if len(message) > 30
            else message[: len(message)]
        )

        client = WebClient(token=token)

        message_to_user = (
            f"Your message has a negative sentiment.\nPlease be kind to others."
        )
        client.chat_postMessage(
            channel=channel,
            text="Sentiment Analysis",
            username=username,
            attachments=[
                {
                    "color": "red",
                    "fields": [
                        {"title": "Message", "value": message, "short": False},
                        {
                            "title": "Sentiment",
                            "value": sentiment_result,
                            "short": False,
                        },
                        {
                            "title": "Message to User",
                            "value": message_to_user,
                            "short": False,
                        },
                    ],
                }
            ],
        )

    return jsonify({}), 200
