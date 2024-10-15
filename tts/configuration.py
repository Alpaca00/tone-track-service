import os


class BaseConfig:
    """Base configuration."""

    SECURITY_PASSWORD_SALT = os.environ.get("SPS")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class ProdConfig(BaseConfig):
    """Production configuration."""

    pass


class TestConfig(BaseConfig):
    """Test configuration."""

    TESTING = True
    DEBUG = True


configurations = {
    "production": ProdConfig,
    "testing": TestConfig,
}
