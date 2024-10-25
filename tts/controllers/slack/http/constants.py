from typing import final

from tts.extensions import config_tts


DEFAULT_SENTIMENT_MESSAGE: final = config_tts.project.default_sentiment_message
SIGNATURE_VERIFICATION_ERROR: final = {"error": "Signature verification failed."}


RESPONSE_ACTION_CLEAR: final = {"response_action": "clear"}

VALIDATION_ERROR_MESSAGE: final = "Validation error occurred."
INVALID_FORM_MESSAGE: final = "Invalid form fields provided."
USER_DATA_NOT_FOUND: final = "User data not found. Please try again."
NO_MESSAGE_FOUND: final = "No message found."

COMMANDS: final = {
    "add": "/tt-add-message",  # Add | Update sentiment analysis message to channel
    "read": "/tt-read-message",  # Retrieve sentiment analysis message from channel
}
