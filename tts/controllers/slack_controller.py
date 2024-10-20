import json
from typing import final

from flask import Blueprint, request, jsonify, redirect
from pydantic import ValidationError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from tts.extensions import env_variables, redis_client
from tts.helpers.constants import EnvironmentVariables
from tts.helpers.decorators import handle_exceptions
from tts.helpers.functions import (
    analyze_sentiment,
    verify_slack_app_signature,
    is_negative_sentiment,
)
from tts.models.postgres.base import DatabaseManager, initialize_database

from tts.models.slack_application import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
    SlackInteractionModalResponse,
    modal_view_callback_id,
    modal_view,
)
from tts.models.slack_application.interaction.add import RedisValuesValidated

slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)
slack_commands = Blueprint("slack_commands", __name__)
slack_interactions = Blueprint("slack_interactions", __name__)

DEFAULT_SENTIMENT_MESSAGE: final = (
    "Your message has a negative sentiment.\nPlease be kind to others."
)

SIGNATURE_VERIFICATION_ERROR: final = {"error": "Signature verification failed."}
EVENT_NOT_FOUND: final = {"error": "Event not found."}

UNSUPPORTED_EVENT_TYPE: final = {"message": "Unsupported event type."}
UNSUPPORTED_COMMAND: final = {"message": "Unsupported command."}
NO_PAYLOAD_PROVIDED: final = {"message": "No payload provided."}

RESPONSE_ACTION_CLEAR: final = {"response_action": "clear"}

VALIDATION_ERROR_MESSAGE: final = "Validation error occurred."
INVALID_FORM_MESSAGE: final = "Invalid form fields provided."
USER_DATA_NOT_FOUND: final = "User data not found. Please try again."
NO_MESSAGE_FOUND: final = "No message found."

COMMANDS: final = {
    "add": "/tt-add-message",  # Add | Update sentiment analysis message to channel
    "read": "/tt-read-message",  # Retrieve sentiment analysis message from channel
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
        redis_values = RedisValuesValidated(**data)

        redis_client.store_user_data_with_ttl(
            user_id=redis_values.user_id,
            team_id=redis_values.team_id,
            team_domain=redis_values.team_domain,
            channel_id=redis_values.channel_id,
            channel_name=redis_values.channel_name,
        )
        return open_modal(data)
    elif command == COMMANDS["read"]:
        return read_message_for_channel(data)

    return jsonify(UNSUPPORTED_COMMAND), 400


@slack_interactions.route("/api/v1/slack/interactions", methods=["POST"])
@handle_exceptions
def slack_app_interaction():
    """Handle interactions from Slack modal."""
    payload = request.form.get("payload")

    if not payload:
        return jsonify(NO_PAYLOAD_PROVIDED), 400

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

    return jsonify(RESPONSE_ACTION_CLEAR)


def verify_signature(request_) -> bool:
    """Verify Slack request signature."""
    signing_secret = env_variables.SLACK_SIGNING_SECRET
    return verify_slack_app_signature(
        signing_secret=signing_secret, request_=request_
    )


def open_modal(data: dict) -> jsonify:
    """Open a Slack modal for adding a channel message."""
    client = WebClient(token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN)
    trigger_id = data.get("trigger_id")

    try:
        client.views_open(trigger_id=trigger_id, view=modal_view.model_dump())
        return jsonify({}), 200
    except SlackApiError as e:
        return jsonify({"error": str(e)}), 500


def read_message_for_channel(data: dict) -> jsonify:
    """Read a sentiment analysis message from a channel."""
    client = WebClient(token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN)
    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    if user_id:
        initialize_database()
        db_manager = DatabaseManager()
        channel_message = db_manager.read_channel_sentiment_message(channel_id)
        client.chat_postMessage(
            channel=channel_id,
            text="Sentiment Analysis",
            mrkdwn=True,
            attachments=[
                {
                    "color": "yellow",
                    "fields": [
                        {
                            "title": "Read Message",
                            "value": channel_message or NO_MESSAGE_FOUND,
                            "short": False,
                        },
                    ],
                }
            ],
        )
    else:
        client.chat_postMessage(channel=channel_id, text=USER_DATA_NOT_FOUND)

    return jsonify({}), 200


def handle_modal_submission(client: WebClient, validated_data) -> jsonify:
    """Handle the submission of a Slack modal."""
    state_values = validated_data.view.state.values
    block = "sentiment_analysis_message_block"
    input_ = "sentiment_analysis_message_input"
    added, updated = "Added", "Updated"

    channel_message = state_values[block][input_].value
    team_id = validated_data.team.id
    team_domain = validated_data.team.domain

    user_data = redis_client.get_user_data(validated_data.user.id)

    def send_message(title: str):
        """Send a message to the channel."""
        nonlocal channel_message, user_data

        client.chat_postMessage(
            channel=user_data["channel_id"],
            text="Sentiment Analysis",
            mrkdwn=True,
            attachments=[
                {
                    "color": "yellow",
                    "fields": [
                        {
                            "title": f"{title} Message",
                            "value": channel_message,
                            "short": False,
                        },
                    ],
                }
            ],
        )

    if not user_data:
        client.chat_postMessage(
            channel=user_data["channel_id"],
            text=USER_DATA_NOT_FOUND,
        )
        return jsonify(RESPONSE_ACTION_CLEAR)

    initialize_database()
    db_manager = DatabaseManager()
    message_exists = db_manager.read_channel_sentiment_message(
        user_data["channel_id"]
    )

    if message_exists:
        db_manager.update_channel_sentiment_message(
            channel_id=user_data["channel_id"], sentiment_message=channel_message
        )
        send_message(title=updated)
    else:
        db_manager.add_channel_sentiment_message(
            team_id=team_id,
            team_domain=team_domain,
            channel_id=user_data["channel_id"],
            channel_name=user_data["channel_name"],
            sentiment_message=channel_message,
        )

        redis_client.delete_user_data(validated_data.user.id)
        send_message(title=added)

    return jsonify(RESPONSE_ACTION_CLEAR)


def handle_validation_error(payload_dict, client: WebClient):
    """Handle validation errors."""
    channel_id = payload_dict.get("user").get("id")
    client.chat_postMessage(channel=channel_id, text=VALIDATION_ERROR_MESSAGE)


def handle_event_callback(data: dict) -> jsonify:
    """Handles the event callback from Slack."""
    event = data.get("event")

    if not event:
        return jsonify(EVENT_NOT_FOUND), 400

    message = event.get("text")
    channel_id = event.get("channel")
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
        initialize_database()
        db_manager = DatabaseManager()

        message_to_user = db_manager.read_channel_sentiment_message(channel_id)

        if not message_to_user:
            message_to_user = DEFAULT_SENTIMENT_MESSAGE
        client.chat_postMessage(
            channel=channel_id,
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
