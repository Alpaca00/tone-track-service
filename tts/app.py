from typing import Literal

from flask import Flask
from flask.testing import FlaskClient
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from tts.configuration import configurations
from tts.controllers import sentiment_bp, health, slack_verification, slack_events


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

    def __init__(self, environment: Literal["production", "testing"] = "testing"):
        self.app = Flask(__name__)
        self.app.config.from_object(configurations[environment])
        Limiter(
            get_remote_address,
            app=self.app,
            default_limits=["60 per minute", "1 per second"],
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
