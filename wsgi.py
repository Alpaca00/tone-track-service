"""WSGI entrypoint.

copyright: (c) by Oleg Matskiv
license: MIT
"""  # noqa

from tts.app import SentimentAnalysisService

app = SentimentAnalysisService(environment="production")
app.run(host="0.0.0.0", port=5000)
