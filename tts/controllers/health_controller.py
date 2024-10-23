from flask import Blueprint, jsonify

health = Blueprint("health", __name__)


@health.route("/api/v1/health", methods=["GET"])
def health_check() -> jsonify:
    """Health check API."""
    return jsonify({"status": "up"}), 200
