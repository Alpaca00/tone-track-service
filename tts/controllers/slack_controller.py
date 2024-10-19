import json

from flask import Blueprint, request, jsonify, redirect
from pydantic import ValidationError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from tts.extensions import env_variables
from tts.helpers.constants import EnvironmentVariables
from tts.helpers.decorators import handle_exceptions
from tts.helpers.functions import (
    analyze_sentiment,
    send_message_to_slack,
    verify_slack_app_signature,
)
from tts.models.slack_app import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
    SlackInteractionModalResponse,
    modal_view,
    modal_view_callback_id,
)


slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)
slack_commands = Blueprint("slack_commands", __name__)
slack_interactions = Blueprint("slack_interactions", __name__)


@slack_events.route("/api/v1/slack/events", methods=["POST"])
@handle_exceptions
def slack_app_events():
    """The endpoint for Slack events orchestration."""
    signing_secret_ = env_variables.SLACK_SIGNING_SECRET
    if not verify_slack_app_signature(
        signing_secret=signing_secret_, request_=request
    ):
        return jsonify({"error": "Signature verification failed."}), 400

    data = request.get_json()

    event_type = data.get("type")
    if event_type == "url_verification":
        return redirect("/api/v1/slack/verification", code=307)
    elif event_type == "event_callback":
        return handle_event_callback(data)

    return jsonify({"message": "Unsupported event type."}), 400


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
def slack_app_commands():
    """The endpoint for Slack commands."""
    signing_secret_ = env_variables.SLACK_SIGNING_SECRET
    if not verify_slack_app_signature(
        signing_secret=signing_secret_, request_=request
    ):
        return jsonify({"error": "Signature verification failed."}), 400
    data = request.form
    command = data.get("command")
    if command == "/tt-add-workspace":
        client = WebClient(token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN)

        trigger_id = data.get("trigger_id")
        try:
            client.views_open(
                trigger_id=trigger_id,
                view=modal_view.model_dump(),
            )
            return jsonify({}), 200
        except SlackApiError:
            return jsonify({}), 200


@slack_interactions.route("/api/v1/slack/interactions", methods=["POST"])
def slack_interaction():
    payload = request.form.get("payload")
    client = WebClient(token=env_variables.SLACK_BOT_OAUTH_TOKEN)
    if payload:
        try:
            payload_dict = json.loads(payload)
            validated_data = SlackInteractionModalResponse(**payload_dict)

            if validated_data.view.callback_id == modal_view_callback_id:

                workspace_name_value = validated_data.view.state.values[
                    "workspace_name_block"
                ]["workspace_name"].value
                workspace_email_value = validated_data.view.state.values[
                    "workspace_email_block"
                ]["workspace_email"].value
                workspace_message = validated_data.view.state.values[
                    "message_reply_block"
                ]["message_reply"].value

                client.chat_postMessage(
                    channel=validated_data.user.id,
                    text=f"> Workspace name: {workspace_name_value}\nWorkspace email: {workspace_email_value}\nSentiment message: {workspace_message}",
                    mrkdwn=True,
                )
            else:
                client.chat_postMessage(
                    channel=validated_data.user.id,
                    text="Invalid form fields provided.",
                )
        except ValidationError:
            payload_dict = json.loads(payload)
            channel_id = payload_dict.get("user").get("id")
            client.chat_postMessage(
                channel=channel_id, text="Validation error occurred."
            )
            return jsonify({}), 200
        except TypeError:
            pass
        finally:
            return jsonify({"response_action": "clear"})

    return jsonify({}), 200


def handle_event_callback(data: dict):
    """Handles the event callback from Slack."""
    event = data.get("event")
    if not event:
        return jsonify({"error": "Event not found."}), 400

    message = event.get("text")
    channel_id = event.get("channel")
    username = event.get("user")

    sentiment_result = analyze_sentiment(message=message)
    response_processed = {
        "text": message,
        "sentiment_result": sentiment_result,
    }
    send_message_to_slack(
        sentiment_result,
        text=message,
        token=env_variables.SLACK_BOT_OAUTH_TOKEN,
        channel=channel_id,
        username=username,
    )
    return jsonify(response_processed), 200
