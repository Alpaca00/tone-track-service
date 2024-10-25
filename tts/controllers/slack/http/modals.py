from flask import jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from tts.controllers.slack.http.constants import (
    USER_DATA_NOT_FOUND,
    RESPONSE_ACTION_CLEAR,
)
from tts.controllers.slack.http.templates import Template
from tts.extensions import client_redis, client_slack
from tts.models.postgres.base import DatabaseManager, initialize_database
from tts.models.slack_application import modal_view


def open_modal(data: dict) -> jsonify:
    """Open a Slack modal for adding a channel message."""
    trigger_id = data.get("trigger_id")
    try:
        client_slack.views_open(
            trigger_id=trigger_id, view=modal_view.model_dump()
        )
        return jsonify({}), 200
    except SlackApiError as e:
        return jsonify({"error": str(e)}), 500


def handle_modal_submission(client: WebClient, validated_data) -> jsonify:
    """Handle the submission of a Slack modal."""
    state_values = validated_data.view.state.values
    block = "sentiment_analysis_message_block"
    input_ = "sentiment_analysis_message_input"
    added, updated = "Added", "Updated"

    channel_message = state_values[block][input_].value
    team_id = validated_data.team.id
    team_domain = validated_data.team.domain

    user_data = client_redis.get_user_data(validated_data.user.id)

    def send_message(title: str):
        """Send a message to the channel."""
        nonlocal channel_message, user_data

        client.chat_postMessage(
            channel=user_data["channel_id"],
            text="Sentiment Analysis",
            mrkdwn=True,
            attachments=Template.build_message_attachments(
                title=title, channel_message=channel_message
            ),
        )

    if not user_data:
        client.chat_postMessage(
            channel=user_data["channel_id"],
            text=USER_DATA_NOT_FOUND,
        )
        return jsonify(RESPONSE_ACTION_CLEAR)

    initialize_database()
    db_manager = DatabaseManager()
    existing_message = db_manager.read_channel_sentiment_message(
        user_data["channel_id"]
    )

    if existing_message:
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

        client_redis.delete_user_data(validated_data.user.id)
        send_message(title=added)

    return jsonify(RESPONSE_ACTION_CLEAR)
