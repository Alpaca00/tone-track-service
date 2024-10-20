import redis
from contextlib import contextmanager

from tts.helpers.constants import EnvironmentVariables


class RedisDatabaseConfig:
    """The database configuration."""

    host = "redis"
    port = 6379
    db = 0
    password = EnvironmentVariables.REDIS_PASSWORD

    @classmethod
    def prepare(cls):
        """Return the database full configuration."""
        return cls.host, cls.port, cls.db, cls.password


class RedisClient:
    def __init__(self):
        self.host, self.port, self.db, self.password = (
            RedisDatabaseConfig.prepare()
        )
        self.connection = None

    def connect(self):
        """Connect to Redis."""
        self.connection = redis.StrictRedis(
            host=self.host, port=self.port, db=self.db, password=self.password
        )

    def close(self):
        """Close the connection."""
        if self.connection:
            del self.connection

    @contextmanager
    def manage_connection(self):
        """Context manager to handle connection."""
        self.connect()
        try:
            yield self.connection
        finally:
            self.close()

    def store_user_data_with_ttl(
        self,
        user_id: str,
        team_id: str,
        team_domain: str,
        channel_id: str,
        channel_name: str,
        ttl_seconds: int = 1800,
    ):
        """Store user data with TTL."""
        with self.manage_connection() as conn:
            user_key = f"user:{user_id}:event_data"
            data = {
                "team_id": team_id,
                "team_domain": team_domain,
                "channel_id": channel_id,
                "channel_name": channel_name,
            }
            conn.hset(user_key, mapping=data)
            conn.expire(user_key, ttl_seconds)

    def get_user_data(self, user_id: str, decoded: bool = True):
        """Get user data."""
        with self.manage_connection() as conn:
            user_key = f"user:{user_id}:event_data"
            if decoded:
                user_data = conn.hgetall(user_key)
                return {
                    key.decode("utf-8"): value.decode("utf-8")
                    for key, value in user_data.items()
                }
            return conn.hgetall(user_key)

    def get_ttl(self, user_id):
        """Get TTL for the user key."""
        with self.manage_connection() as conn:
            user_key = f"user:{user_id}:event_data"
            return conn.ttl(user_key)

    def delete_user_data(self, user_id):
        """Delete user data."""
        with self.manage_connection() as conn:
            user_key = f"user:{user_id}:event_data"
            conn.delete(user_key)
