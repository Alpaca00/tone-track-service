from flask import Blueprint, request, jsonify, redirect

from tts.extensions import env_variables
from tts.helpers.decorators import handle_exceptions
from tts.helpers.functions import analyze_sentiment, send_message_to_slack
from tts.models.slack_app import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
)


slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)


@slack_events.route("/api/v1/slack/events", methods=["POST"])
@handle_exceptions
def slack_app_events():
    """The endpoint for Slack events orchestration."""
    data = request.get_json()

    event_type = data.get("type")
    if event_type == "url_verification":
        return redirect_to_url_verification()
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


def redirect_to_url_verification():
    """Redirects to the URL verification endpoint."""
    return redirect("/api/v1/slack/verification", code=307)


def handle_event_callback(data: dict):
    """Handles the event callback from Slack."""
    event = data.get("event")
    if not event:
        return jsonify({"error": "Event not found."}), 400

    # TODO: Implement the logic for verifying the event
    # https://api.slack.com/authentication/verifying-requests-from-slack

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
