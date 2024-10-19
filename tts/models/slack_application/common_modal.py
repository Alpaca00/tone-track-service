from typing import final

from pydantic import BaseModel, Field



class ModalView(BaseModel):
    type: str = Field(default="modal")
    title: dict[str, any] = Field(default_factory=lambda: {"type": "plain_text", "text": "Add Workspace", "emoji": True})
    submit: dict[str, any] = Field(default_factory=lambda: {"type": "plain_text", "text": "Submit", "emoji": True})
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
        "block_id": "workspace_name_block",
        "label": {
            "type": "plain_text",
            "text": "Workspace Name",
            "emoji": True
        },
        "element": {
            "type": "plain_text_input",
            "action_id": "workspace_name",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter your workspace name"
            }
        }
    },
    {
        "type": "input",
        "block_id": "workspace_email_block",
        "label": {
            "type": "plain_text",
            "text": "Workspace Email",
            "emoji": True
        },
        "element": {
            "type": "plain_text_input",
            "action_id": "workspace_email",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter your workspace email"
            }
        }
    },
    {
        "type": "input",
        "block_id": "message_reply_block",
        "label": {
            "type": "plain_text",
            "text": "Sentiment Analysis Message",
            "emoji": True
        },
        "element": {
            "type": "plain_text_input",
            "action_id": "message_reply",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter your message for sentiment analysis"
            }
        }
    },
])
