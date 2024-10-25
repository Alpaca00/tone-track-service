import urllib
from typing import Optional
from urllib.parse import urlencode

from flask import request, jsonify
from slack_sdk.signature import SignatureVerifier

from tts.controllers.slack.http.constants import SIGNATURE_VERIFICATION_ERROR
from tts.extensions import env_variables


def is_valid_signature(request_: request) -> bool:
    """Check if the request signature is valid."""
    verifier = SignatureVerifier(env_variables.SLACK_SIGNING_SECRET)

    request_body = request_.get_json()
    body = "&".join(
        [
            "=".join([key, urllib.parse.quote_plus(str(val))])
            for key, val in request_body.items()
        ]
    )
    return verifier.is_valid_request(body, request_.headers)


def validate_request_signature(request_: request) -> Optional[tuple]:
    """Validate the request signature."""
    if not is_valid_signature(request_):
        return jsonify(SIGNATURE_VERIFICATION_ERROR), 403
