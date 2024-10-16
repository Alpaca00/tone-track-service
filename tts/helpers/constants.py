import os

from dotenv import load_dotenv

load_dotenv()

class EnvironmentVariables:
    """Environment variables."""
    API_KEY = os.environ.get("API_KEY")
    SLACK_BOT_OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
