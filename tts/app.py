import ast
from typing import Literal

from flask import Flask, render_template, request, jsonify, Response
from flask.testing import FlaskClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from tts.controllers import (
    sentiment_bp,
    proxy_sentiment_bp,
    health,
    slack_verification,
    slack_events,
    slack_commands,
    slack_interactions,
)
from tts.extensions import config_tts, configurations


class Monostate:
    """Monostate class to share state among instances."""

    _state: dict[str, any] = {}

    def __getattr__(self, name: str) -> any:
        """Get the value of an attribute from the shared state."""
        return self._state.get(name)

    def __setattr__(self, name: str, value: any) -> None:
        """Set the value of an attribute in the shared state."""
        self._state[name] = value


class SentimentAnalysisService(Monostate):
    """Main class for the sentiment analysis Flask application."""

    def __init__(self, environment: Literal["production", "testing"]):
        self.app = Flask(__name__, template_folder="static")
        if environment not in ("production", "testing"):
            environment = config_tts.project.environment
        self.app.config.from_object(configurations[environment])
        minute, second = ast.literal_eval(config_tts.project.rate_limiter)
        web_interface = ast.literal_eval(config_tts.project.web_interface)
        Limiter(
            get_remote_address,
            app=self.app,
            default_limits=[f"{minute} per minute", f"{second} per second"],
            storage_uri="memory://",
        )
        self.configure_service()
        self.block_attack_vector()
        if web_interface:
            CORS(
                self.app,
                resources={
                    r"/api/*": {
                        "origins": "https://tone-track.uno",
                        "methods": ["GET", "POST", "OPTIONS"],
                    },
                },
                allow_headers=["Content-Type", "Authorization"],
            )
            self.setup_web_route()

    def configure_service(self) -> None:
        """Register the blueprint for the controller."""
        register_blueprints = (
            health,
            sentiment_bp,
            proxy_sentiment_bp,
            slack_verification,
            slack_events,
            slack_commands,
            slack_interactions,
        )
        for blueprint in register_blueprints:
            self.app.register_blueprint(blueprint)

    def setup_web_route(self):
        """Setup the web route for the application."""

        @self.app.route("/")
        def web_resource() -> tuple[str, int]:
            """Return the Page rendered by the template."""
            return render_template("base.html"), 200

    def block_attack_vector(self) -> None:
        """Block attack vectors from being accessed."""

        @self.app.before_request
        def attack_vector() -> tuple[Response, int]:
            message = config_tts.project.attack_vector_message
            sensitive_files = [
                "/.env",
                "/.envi",
                "/.env.bak",
                "/.env.swp",
                "/.env.tmp",
                "/.git",
                "/.gitignore",
                "/.gitmodules",
                "/.gitkeep",
                "/.gitlab-ci.yml",
                "/.hg",
                "/config.php",
                "/backup.sql",
                "/wp-config.php",
                "/env.txt",
                "/envi.txt",
                "/config.txt",
                "/config.ini",
            ]
            if any(request.path.startswith(file) for file in sensitive_files):
                return jsonify({"message": message}), 403

    def test_client(self) -> FlaskClient:
        """Create a test client for the application."""
        if self.environment == "production":
            raise ValueError("Cannot create a test client in production.")
        return self.app.test_client()

    def run(self, *args, **kwargs) -> None:
        """Run the Flask application."""
        self.app.run(*args, **kwargs)

    def __call__(self, environ, start_response) -> any:
        """Make the instance callable."""
        return self.app(environ, start_response)
