import os

from dotenv import load_dotenv

load_dotenv()

class EnvironmentVariables:
    """Environment variables."""
    # FLASK
    API_KEY = os.environ.get("API_KEY")
    # TODO: Get the token from the database after the workspace is added
    SLACK_BOT_OAUTH_TOKEN = os.environ.get("SLACK_BOT_OAUTH_TOKEN")
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
    # DATABASE
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB = os.environ.get("POSTGRES_DB")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST")