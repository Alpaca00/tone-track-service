from flask import Blueprint

slack_events = Blueprint("slack_events", __name__)


@slack_events.route("api/v1/slack-events", methods=["POST"])
def slack_events():
    """Slack events API."""
    pass
