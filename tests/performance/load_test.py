import os

from locust import task, FastHttpUser, LoadTestShape

from tests.performance.helpers import JSONFileIteratorSentimentAnalysisPayload
from tests.performance.routes import Routes


LOCUST_RUN_TIME = int(os.environ.get("LOCUST_RUN_TIME", 600))


class LoadTest(FastHttpUser):
    """Load testing for 2 endpoints and 1 template.

    vCPU: 3
    Memory: 4 GB

    Rate limit: 10 requests per second.
    """

    min_wait = 2000
    max_wait = 5000
    network_timeout = 10.0
    connection_timeout = 10.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routes = Routes(client=self.client)
        self.file_iterator = JSONFileIteratorSentimentAnalysisPayload(
            "tests/performance/data/load_test.json"
        )

    @task
    def health(self):
        """GET api/v1/health."""
        self.routes.health()

    @task
    def main(self):
        """GET /."""
        self.routes.main()

    @task(2)
    def proxy_positive_sentiment_analysis(self):
        """POST api/v1/sentiment-analysis."""
        data = self.file_iterator.get_next_positive()
        self.routes.proxy_sentiment_analysis(data=data)

    @task(2)
    def proxy_negative_sentiment_analysis(self):
        """POST api/v1/sentiment-analysis."""
        data = self.file_iterator.get_next_negative()
        self.routes.proxy_sentiment_analysis(data=data)


class CustomLoadShape(LoadTestShape):
    """Custom load shape for gradual RPS growth."""

    def tick(self):
        """Determines the number of users at a given time and the rate at which users are spawned."""
        run_time = self.get_run_time()

        if run_time > LOCUST_RUN_TIME:
            return

        if run_time < 300:
            user_count = run_time // 10
            spawn_rate = 1
        else:
            user_count = 30
            spawn_rate = 2

        return user_count, spawn_rate
