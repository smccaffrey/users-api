from fastapi.testclient import TestClient

from tests.conftest import TEST_AUTH_HEADERS


# TODO: Replace these routes with your routes
def test_health_check_route(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200  # noqa: PLR2004


def test_create_car_route(client: TestClient) -> None:
    request_body = {"color": "blue", "brand": "bmw", "is_preowned": False}
    response = client.post("/car", headers=TEST_AUTH_HEADERS, json=request_body)
    assert response.status_code == 200  # noqa: PLR2004

    assert response.json()["data"]["color"] == "blue"
    assert response.json()["data"]["brand"] == "bmw"
    assert response.json()["data"]["is_preowned"] is False
