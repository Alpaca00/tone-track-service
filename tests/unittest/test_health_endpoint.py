import pytest

from tests.constants import Endpoint


@pytest.mark.health_unittest
def test_health_check(client):
    """Test the health check API."""
    response = client.get(Endpoint.HEALTH)
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["status"] == "up"
