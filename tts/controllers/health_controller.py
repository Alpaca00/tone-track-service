from flask import Blueprint, jsonify

health = Blueprint("health", __name__)


@health.route("/api/v1/health", methods=["GET"])
def health_check() -> jsonify:
    """Health check API.

    :returns: JSON object with the status of the service.
    """
    return jsonify({"status": "up"}), 200
