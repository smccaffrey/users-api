import uuid

from starlette.testclient import TestClient

from todo_name_service.constants import HTTP_HEADER_REQUEST_ID


def test_request_id_set(client: TestClient) -> None:
    resp = client.get("/")
    assert HTTP_HEADER_REQUEST_ID.lower() == "x-pinwheel-request-id"
    assert HTTP_HEADER_REQUEST_ID in resp.headers
    assert uuid.UUID(resp.headers[HTTP_HEADER_REQUEST_ID])
