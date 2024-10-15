import logging
import uuid

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from _pytest.logging import LogCaptureFixture
from shared_python.logger.logger import PinwheelLogger
from starlette.testclient import TestClient

from tests.conftest import TEST_AUTH_HEADERS
from todo_name_service.api.exceptions import APIErrorCode, APIErrorType
from todo_name_service.constants import HTTP_HEADER_REQUEST_ID


@pytest.fixture()
def enable_route_logger_caplog() -> Generator[None, None, None]:
    # Enable caplog
    # https://stackoverflow.com/questions/61702794/
    # pytest-capture-not-working-caplog-and-capsys-are-empty
    route_logger = PinwheelLogger("todo_name_service.middleware.request_logger").logger
    route_logger.propagate = True

    yield

    route_logger.propagate = False


class _UniqueTestError(Exception):
    pass


@patch("todo_name_service.api.routes.car_manager.create", side_effect=_UniqueTestError)
def test_uncaught_exceptions_handled(
    _: MagicMock,
    client_no_exceptions: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    """
    Random endpoint that we'll throw an error for. Need to init a special
        test client to validate the 500
    """
    caplog.set_level(logging.INFO)

    request_body = {"color": "blue", "brand": "bmw", "is_preowned": False}
    resp = client_no_exceptions.post("/car", headers=TEST_AUTH_HEADERS, json=request_body)

    assert resp.status_code == 500  # noqa: PLR2004
    assert resp.json()["error"]["code"] == APIErrorCode.UNKNOWN_ERROR.value
    assert resp.json()["error"]["type"] == APIErrorType.UNKNOWN_ERROR.value
    exception_logs = [r for r in caplog.records if getattr(r, "error", None)]
    assert len(exception_logs) == 1
    assert isinstance(exception_logs[0].error, _UniqueTestError)
    assert HTTP_HEADER_REQUEST_ID.lower() == "x-pinwheel-request-id"
    assert HTTP_HEADER_REQUEST_ID in resp.headers
    assert uuid.UUID(resp.headers[HTTP_HEADER_REQUEST_ID])


def test_invalid_endpoint_404(client_no_exceptions: TestClient) -> None:
    resp = client_no_exceptions.get("/i-promise-this-does-not-exist", headers=TEST_AUTH_HEADERS)

    assert resp.status_code == 404  # noqa: PLR2004
    assert resp.json()["error"]["code"] == APIErrorCode.ENDPOINT_NOT_FOUND.value
    assert resp.json()["error"]["type"] == APIErrorType.RECORD_NOT_FOUND.value
    assert HTTP_HEADER_REQUEST_ID.lower() == "x-pinwheel-request-id"
    assert HTTP_HEADER_REQUEST_ID in resp.headers
    assert uuid.UUID(resp.headers[HTTP_HEADER_REQUEST_ID])


def test_invalid_endpoint_method_405(client_no_exceptions: TestClient) -> None:
    resp = client_no_exceptions.post("/", headers=TEST_AUTH_HEADERS)

    assert resp.status_code == 405  # noqa: PLR2004
    assert resp.json()["error"]["code"] == APIErrorCode.METHOD_NOT_ALLOWED.value
    assert resp.json()["error"]["type"] == APIErrorType.INVALID_REQUEST_PARAMETERS.value
    assert HTTP_HEADER_REQUEST_ID.lower() == "x-pinwheel-request-id"
    assert HTTP_HEADER_REQUEST_ID in resp.headers
    assert uuid.UUID(resp.headers[HTTP_HEADER_REQUEST_ID])
