from flask import Blueprint, request

from tts.models.slack_app import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
)

slack_verification = Blueprint("slack_verification", __name__)


@slack_verification.route("/api/v1/slack/verification", methods=["POST"])
def slack_events():
    """Slack events API."""
    data = request.get_json()
    slack_request = SlackVerificationRequest(**data)

    response = SlackVerificationChallengeResponse(
        challenge=slack_request.challenge
    )
    return response.model_dump_json()
