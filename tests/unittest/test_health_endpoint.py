import pytest


@pytest.mark.health
def test_health_check(client):
    """Test the health check API."""
    response = client.get("/api/v1/health")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["status"] == "up"
