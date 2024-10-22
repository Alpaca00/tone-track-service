from functools import wraps
from flask import jsonify, request, current_app
from pydantic import ValidationError

from tts.helpers.constants import EnvironmentVariables


def handle_exceptions(func):
    """Handle exceptions in the API."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({"error": e.errors()}), 422
        except IndexError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return wrapper


def require_api_key(func):
    """Require an API key to access the API."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if (
            api_key != EnvironmentVariables.API_KEY
            and current_app.config["TESTING"] is False
        ):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    return decorated_function


def ip_whitelist(func):
    """Check if the client IP is in the whitelist."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in current_app.config["ALLOWED_IPS"]:
            return jsonify({"error": "Forbidden: Your IP is not allowed"}), 403

        return func(*args, **kwargs)

    return decorated_function
