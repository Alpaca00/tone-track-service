import ast
from typing import Literal

from flask import Flask
from flask.testing import FlaskClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from tts.controllers import (
    sentiment_bp,
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
        self.app = Flask(__name__)
        if environment not in ("production", "testing"):
            environment = config_tts.project.environment
        self.app.config.from_object(configurations[environment])
        minute, second = ast.literal_eval(config_tts.project.rate_limiter)
        Limiter(
            get_remote_address,
            app=self.app,
            default_limits=[f"{minute} per minute", f"{second} per second"],
            storage_uri="memory://",
        )
        self.configure_service()

    def configure_service(self) -> None:
        """Register the blueprint for the controller."""
        register_blueprints = (
            health,
            sentiment_bp,
            slack_verification,
            slack_events,
            slack_commands,
            slack_interactions,
        )
        for blueprint in register_blueprints:
            self.app.register_blueprint(blueprint)

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
