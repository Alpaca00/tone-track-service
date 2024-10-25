class Template:
    """Base class for templates."""

    @staticmethod
    def build_sentiment_attachments(**kwargs):
        """Return a list of attachments."""
        message = kwargs.get("message")
        sentiment_result = kwargs.get("sentiment_result")
        message_to_user = kwargs.get("message_to_user")
        return [
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
        ]

    @staticmethod
    def build_message_attachments(title: str, **kwargs):
        """Return a list of attachments with a specified title."""
        channel_message = kwargs.get("channel_message")
        return [
            {
                "color": "yellow",
                "fields": [
                    {
                        "title": title,
                        "value": channel_message,
                        "short": False,
                    },
                ],
            }
        ]
