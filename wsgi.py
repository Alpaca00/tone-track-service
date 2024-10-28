"""WSGI entrypoint.

copyright: (c) by Oleg Matskiv
license: Apache License 2.0
"""  # noqa

from tts.app import SentimentAnalysisService
from tts.extensions import config_tts as config


app = SentimentAnalysisService(environment=config.project.environment)


if __name__ == "__main__":
    app.run(
        host=config.resources.interface,
        port=config.resources.port,
        debug=config.project.debug,
    )
