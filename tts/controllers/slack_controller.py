import random

import requests
from flask import Blueprint, request, jsonify, redirect
from langdetect import detect, DetectorFactory, LangDetectException
from slack_sdk import WebClient

from tts.helpers.constants import EnvironmentVariables
from tts.helpers.decorators import handle_exceptions
from tts.helpers.functions import Config
from tts.models.slack_app import (
    SlackVerificationRequest,
    SlackVerificationChallengeResponse,
)


DetectorFactory.seed = 0
slack_events = Blueprint("slack_events", __name__)
slack_verification = Blueprint("slack_verification", __name__)


@slack_events.route("/api/v1/slack/events", methods=["POST"])
@handle_exceptions
def slack_app_events():
    """The endpoint for Slack events orchestration."""
    data = request.get_json()

    event_type = data.get("type")
    if event_type == "url_verification":
        return redirect_to_url_verification(data)
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


def redirect_to_url_verification(data):
    """Redirects to the URL verification endpoint."""
    return redirect("/api/v1/slack/verification", code=307)


def handle_event_callback(data: dict):
    """Handles the event callback from Slack."""
    event = data.get("event")
    if not event:
        return jsonify({"error": "Event not found."}), 400

    message = event.get("text")
    channel_id = event.get("channel")
    username = event.get("user")

    # if not is_english(message):
    #     return jsonify({"message": "Only English messages are supported."}), 200

    sentiment_result = analyze_sentiment(message)
    response_processed = {
        "text": message,
        "sentiment_result": sentiment_result,
    }
    send_message_to_slack(
        sentiment_result,
        text=message,
        token=EnvironmentVariables.SLACK_BOT_OAUTH_TOKEN,
        channel=channel_id,
        username=username,
    )
    return jsonify(response_processed), 200


def send_message_to_slack(sentiment_result: str, **kwargs):
    """Sends a message to Slack."""
    message = kwargs.get("text")
    token = kwargs.get("token")
    channel = kwargs.get("channel")
    username = kwargs.get("username")
    if is_negative_sentiment(sentiment_result) and token and message:
        messages = (
            "> This message has a negative sentiment. Please be kind to others. \n",
            "> It seems this message carries a negative tone. Let's keep things positive and constructive! \n",
            "> This message may come across as negative. A little kindness can go a long way! \n",
            "> Your message seems to have a negative sentiment. Let’s focus on solutions and positivity! \n",
        )
        message = random.choice(messages)
        client = WebClient(token=token)
        client.chat_postMessage(
            channel=channel, text=message, mrkdwn=True, username=username
        )


def is_negative_sentiment(sentiment_result: str) -> bool:
    """Checks if the sentiment is negative."""
    return "negative" in sentiment_result and "not" not in sentiment_result


def is_english(text: str) -> bool:
    """Checks if the given text is in English."""
    try:
        language = detect(text)
        return language == "en"
    except (LangDetectException, Exception) as e:
        if isinstance(e, LangDetectException):
            return False
        return True


def analyze_sentiment(message: str,) -> str:
    """Sends a request for sentiment analysis."""
    config = Config()
    url = config.resources.internal_server_url

    response = requests.post(
        f"{url}/api/v1/sentiment-analysis",
        json={
            "text": message,
            "sentiment_type": config.project.sentiment_type,
        },
        headers={"Authorization": EnvironmentVariables.API_KEY},
    )
    response.raise_for_status()
    return response.json().get("sentiment_result")
