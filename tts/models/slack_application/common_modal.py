from typing import final

from pydantic import BaseModel, Field


class ModalView(BaseModel):
    type: str = Field(default="modal")
    title: dict[str, any] = Field(
        default_factory=lambda: {
            "type": "plain_text",
            "text": "Add Message",
            "emoji": True,
        }
    )
    submit: dict[str, any] = Field(
        default_factory=lambda: {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True,
        }
    )
    callback_id: str
    blocks: list[dict[str, any]]

    class Config:
        arbitrary_types_allowed = True


modal_view_callback_id: final = "modal-identifier"
modal_view = ModalView(
    callback_id=modal_view_callback_id,
    blocks=[
        {
            "type": "input",
            "block_id": "sentiment_analysis_message_block",
            "label": {
                "type": "plain_text",
                "text": "Sentiment Analysis Message",
                "emoji": True,
            },
            "element": {
                "type": "plain_text_input",
                "action_id": "sentiment_analysis_message_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Enter your message for sentiment analysis",
                },
            },
        },
    ],
)
