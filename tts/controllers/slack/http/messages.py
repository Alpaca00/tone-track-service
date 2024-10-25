from flask import jsonify

from tts.controllers.slack.http.constants import (
    NO_MESSAGE_FOUND,
    USER_DATA_NOT_FOUND,
)
from tts.controllers.slack.http.templates import Template
from tts.extensions import client_slack
from tts.models.postgres.base import initialize_database, DatabaseManager


def read_message_for_channel(data: dict) -> tuple:
    """Read a sentiment analysis message from a channel."""

    user_id = data.get("user_id")
    channel_id = data.get("channel_id")
    if user_id:
        initialize_database()
        db_manager = DatabaseManager()

        channel_message = db_manager.read_channel_sentiment_message(channel_id)
        client_slack.chat_postMessage(
            channel=channel_id,
            text="Sentiment Analysis",
            mrkdwn=True,
            attachments=Template.build_message_attachments(
                title="Read Message",
                channel_message=channel_message or NO_MESSAGE_FOUND,
            ),
        )
    else:
        client_slack.chat_postMessage(
            channel=channel_id, text=USER_DATA_NOT_FOUND
        )

    return jsonify({}), 200
