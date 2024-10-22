import ast
import os

from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base configuration."""

    SECURITY_PASSWORD_SALT = os.environ.get("SPS")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALLOWED_IPS = ast.literal_eval(os.environ.get("ALLOWED_IPS"))


class ProdConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    DEBUG = False


class TestConfig(BaseConfig):
    """Test configuration."""

    TESTING = True
    DEBUG = True
