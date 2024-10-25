from flask import jsonify

from tts.controllers.slack.http.constants import DEFAULT_SENTIMENT_MESSAGE
from tts.controllers.slack.http.templates import Template
from tts.extensions import client_slack
from tts.helpers.functions import analyze_sentiment, is_negative_sentiment
from tts.models.postgres.base import initialize_database, DatabaseManager


def handle_event_callback(data: dict) -> tuple:
    """Handles the event callback from Slack."""
    event = data.get("event")

    message = event.get("text")
    channel_id = event.get("channel")
    username = event.get("user")

    sentiment_result = analyze_sentiment(message=message)
    if is_negative_sentiment(sentiment_result) and message and channel_id:
        message = (
            message[0:30] + " ..."
            if len(message) > 30
            else message[: len(message)]
        )

        initialize_database()
        db_manager = DatabaseManager()

        existing_message = db_manager.read_channel_sentiment_message(channel_id)

        if not existing_message:
            existing_message = DEFAULT_SENTIMENT_MESSAGE
        client_slack.chat_postMessage(
            channel=channel_id,
            text="Sentiment Analysis",
            username=username,
            attachments=Template.build_sentiment_attachments(
                message=message,
                sentiment_result=sentiment_result,
                message_to_user=existing_message,
            )
        )

    return jsonify({}), 200
