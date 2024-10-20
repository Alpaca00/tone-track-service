from pydantic import BaseModel, constr


class SlackVerificationRequest(BaseModel):
    """Model for Slack URL verification request."""

    token: constr(min_length=10)
    challenge: constr(min_length=10)
    type: constr(strip_whitespace=True, pattern=r"^url_verification$")



class SlackVerificationChallengeResponse(BaseModel):
    """Model for Slack URL verification challenge response."""
    challenge: constr(min_length=10)