from typing import final

from tts.configuration import ProdConfig, TestConfig
from tts.helpers.common import Config
from tts.helpers.constants import EnvironmentVariables
from tts.models.redis.client import RedisClient

config_tts: final = Config()
env_variables: final = EnvironmentVariables()
redis_client: final = RedisClient()

configurations = {
    "production": ProdConfig,
    "testing": TestConfig,
}
