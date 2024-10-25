from typing import final

from slack_sdk import WebClient

from tts.configuration import ProdConfig, TestConfig
from tts.helpers.common import Config
from tts.helpers.constants import EnvironmentVariables
from tts.models.redis.client import RedisClient


config_tts: final = Config()
env_variables: final = EnvironmentVariables()

client_redis: final = RedisClient()
client_slack = WebClient(token=env_variables.SLACK_BOT_OAUTH_TOKEN)

configurations = {
    "production": ProdConfig,
    "testing": TestConfig,
}
