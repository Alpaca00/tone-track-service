"""WSGI entrypoint.

copyright: (c) by Oleg Matskiv
license: MIT
"""  # noqa

from tts.app import SentimentAnalysisService
from tts.helpers.functions import Config

config = Config()

app = SentimentAnalysisService(environment=config.project.environment)
if __name__ == '__main__':
    app.run(
        host=config.resources.interface,
        port=config.resources.port,
        debug=config.project.debug,
    )
