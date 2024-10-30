import pytest

from tts.helpers.constants import EnvironmentVariables
from tts.models.redis.client import RedisClient


@pytest.fixture
def redis_client():
    """Fixture to create RedisClient instance."""
    return RedisClient()


@pytest.fixture
def mock_redis(mocker):
    """Mock the StrictRedis connection."""
    mock_redis_instance = mocker.patch("redis.StrictRedis", autospec=True)
    return mock_redis_instance.return_value


@pytest.mark.redis_client_unittest
def test_connect(redis_client, mocker):
    """Test Redis connection is established."""
    import redis

    mock_redis_instance = mocker.patch.object(redis, "StrictRedis", autospec=True)
    redis_client.connect()

    mock_redis_instance.assert_called_once_with(
        host=EnvironmentVariables.REDIS_HOST,
        port=int(EnvironmentVariables.REDIS_PORT),
        db=0,
        password=EnvironmentVariables.REDIS_PASSWORD,
    )

@pytest.mark.redis_client_unittest
def test_close(redis_client, mock_redis):
    """Test Redis connection is closed."""
    redis_client.manage_connection()
    assert redis_client.connection is None

@pytest.mark.redis_client_unittest
def test_store_user_data_with_ttl(redis_client, mock_redis):
    """Test storing user data with TTL."""
    user_data = {
        "user_id": "U123",
        "team_id": "T123",
        "team_domain": "example.com",
        "channel_id": "C123",
        "channel_name": "general",
    }
    redis_client.store_user_data_with_ttl(**user_data, ttl_seconds=1800)
    user_key = f"user:{user_data['user_id']}:event_data"

    mock_redis.hset.assert_called_once_with(
        user_key,
        mapping={
            "team_id": user_data["team_id"],
            "team_domain": user_data["team_domain"],
            "channel_id": user_data["channel_id"],
            "channel_name": user_data["channel_name"],
        },
    )
    mock_redis.expire.assert_called_once_with(user_key, 1800)

@pytest.mark.redis_client_unittest
def test_get_user_data(redis_client, mock_redis):
    """Test retrieving user data."""
    user_id = "U123"
    user_key = f"user:{user_id}:event_data"

    mock_redis.hgetall.return_value = {
        b"team_id": b"T123",
        b"team_domain": b"example.com",
        b"channel_id": b"C123",
        b"channel_name": b"general",
    }

    result = redis_client.get_user_data(user_id)

    assert result == {
        "team_id": "T123",
        "team_domain": "example.com",
        "channel_id": "C123",
        "channel_name": "general",
    }
    mock_redis.hgetall.assert_called_once_with(user_key)

@pytest.mark.redis_client_unittest
def test_get_ttl(redis_client, mock_redis):
    """Test retrieving TTL of user key."""
    user_id = "U123"
    user_key = f"user:{user_id}:event_data"

    mock_redis.ttl.return_value = 1800
    ttl = redis_client.get_ttl(user_id)

    assert ttl == 1800
    mock_redis.ttl.assert_called_once_with(user_key)

@pytest.mark.redis_client_unittest
def test_delete_user_data(redis_client, mock_redis):
    """Test deleting user data."""
    user_id = "U123"
    user_key = f"user:{user_id}:event_data"

    redis_client.delete_user_data(user_id)
    mock_redis.delete.assert_called_once_with(user_key)
