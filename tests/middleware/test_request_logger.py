import collections.abc
import json
import logging

from http import HTTPStatus
from typing import Any, ContextManager, Dict, Generator
from unittest import mock
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qsl

import pytest

from _pytest.logging import LogCaptureFixture
from shared_python.logger.logger import PinwheelLogger
from starlette.datastructures import QueryParams
from starlette.testclient import TestClient

from tests.conftest import TEST_AUTH_HEADERS
from todo_name_service.middleware.request_logger import (
    _generate_query_params_blob,
    _trim_response_body,
)
from todo_name_service.utils.helper_functions import find


# Get the middleware request logger by using the same namespace
# Get the underlying logger which is the same instance as the route logger
route_logger = PinwheelLogger("todo_name_service.middleware.request_logger").logger


@pytest.fixture()
def enable_route_logger_caplog() -> Generator[None, None, None]:
    # Enable caplog
    # https://stackoverflow.com/questions/61702794/
    # pytest-capture-not-working-caplog-and-capsys-are-empty
    route_logger.propagate = True

    yield

    route_logger.propagate = False


@patch.object(route_logger, "info")
def test_logs_successful_route_handler(mock_log_info: MagicMock, client: TestClient) -> None:
    client.post("/post", headers=TEST_AUTH_HEADERS)
    mock_log_info.assert_called_once()


@patch.object(route_logger, "info")
def test_no_healthcheck_logs(mock_log_info: MagicMock, client: TestClient) -> None:
    client.get("/")
    mock_log_info.assert_not_called()


@patch.object(route_logger, "info")
def test_logs_tracking_ids(mock_log_info: MagicMock, client: TestClient) -> None:
    with patch("todo_name_service.middleware.request_logger._is_health_check", return_value=False):
        client.get("/")
    mock_log_info.assert_called_once()
    expected = {"tracking_id": "tracking_id"}
    actual = mock_log_info.call_args.kwargs["extra"]["tracking_ids"]
    assert actual == expected


def test_logs_pinwheel_http_exception_route_handler(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    client.get("/private/v1/api_key/DOES_NOT_EXIST", headers=TEST_AUTH_HEADERS)

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.status_code == 404  # noqa: PLR2004


def test_logs_request_validation_exception_route_handler(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    # Create bad payload
    api_key_update_payload = {"weird_param": False}

    client.post(
        "/car",
        json=api_key_update_payload,
        headers=TEST_AUTH_HEADERS,
    )

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.status_code == HTTPStatus.BAD_REQUEST
    assert log_request_record.response_body == {
        "error": {
            "type": "INVALID_REQUEST_PARAMETERS",
            "code": "MISSING_FIELDS",
            "status_code": 400,
            "message": "Request is missing required fields: [brand, color, is_preowned].",
            "fields": [
                {"name": "brand", "message": "Field required."},
                {"name": "color", "message": "Field required."},
                {"name": "is_preowned", "message": "Field required."},
            ],
        }
    }


def test_logs_request_validation_exception_route_handler_enum(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    # Create bad payload
    api_key_update_payload = {"brand": "toyota", "color": "not_a_color", "is_preowned": False}

    client.post(
        "/car",
        json=api_key_update_payload,
        headers=TEST_AUTH_HEADERS,
    )

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.status_code == HTTPStatus.BAD_REQUEST
    assert log_request_record.response_body == {
        "error": {
            "code": "INVALID_COLOR",
            "fields": [
                {
                    "message": "Value is not a valid enumeration member; permitted: 'red', 'blue'.",
                    "name": "color",
                }
            ],
            "message": "Validation error.",
            "status_code": 400,
            "type": "INVALID_REQUEST_PARAMETERS",
        }
    }


def test_logs_invalid_method(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    client.delete("/", headers=TEST_AUTH_HEADERS)

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.status_code == 405  # noqa: PLR2004


def test_logs_invalid_route(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    client.post("/v1/a_route_that_doesnt_exist/", headers=TEST_AUTH_HEADERS)

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.status_code == 404  # noqa: PLR2004


def test_trim_response_body_list() -> None:
    fake = {"data": [{"foo": "bar"}, {"bar": "baz"}]}
    assert fake == _trim_response_body(fake)

    with mock.patch("todo_name_service.middleware.request_logger.MAX_LOG_RESPONSE_BODY_SIZE", 100):
        assert {"data": [{"foo": "bar"}, "<TRUNCATED>"]} == _trim_response_body(fake)

    with mock.patch("todo_name_service.middleware.request_logger.MAX_LOG_RESPONSE_BODY_SIZE", 0):
        assert {"data": ["<TRUNCATED>"]} == _trim_response_body(fake)


def test_trim_response_body_not_list() -> None:
    no_list_data = {"data": {"foo": "bar"}}
    with mock.patch("todo_name_service.middleware.request_logger.MAX_LOG_RESPONSE_BODY_SIZE", 0):
        assert _trim_response_body(no_list_data) == no_list_data


@pytest.mark.parametrize(
    "query,expected",
    [
        ("", {}),
        ("foo=bar", dict(foo="bar")),
        ("foo=bar&foobar=barbaz", dict(foo="bar", foobar="barbaz")),
        ("foo=bar&foo=baz&foobar=barbaz", dict(foo="bar, baz", foobar="barbaz")),
        (
            "foo=zzz&foo=kkk&foo=aaa&foobar=barbaz",
            dict(foo="aaa, kkk, zzz", foobar="barbaz"),
        ),
    ],
)
def test_generate_query_params_blob(query: str, expected: Dict[str, str]) -> None:
    query_params = QueryParams(parse_qsl(query, keep_blank_values=True))
    assert _generate_query_params_blob(query_params) == expected


@patch.object(route_logger, "info")
def test_logs_query_params(mock_log_info: MagicMock, client: TestClient) -> None:
    path = "/"
    params = {
        "q": "my_platform",
        "supported_jobs": ["income", "identity", "employment"],
    }
    with patch("todo_name_service.middleware.request_logger._is_health_check", return_value=False):
        client.get(path, params=params)
    mock_log_info.assert_called_once()
    assert mock_log_info.call_args.kwargs["extra"]["request_query_params_blob"] == dict(
        q="my_platform", supported_jobs="employment, identity, income"
    )


@pytest.mark.parametrize(
    "data,expected_request_body_raw,expected_request_body",
    [
        ("", "", None),
        ("{an invalid json object", "{an invalid json object", None),
        ("🐙", "🐙", None),
        ({}, "{}", {}),
        ({"job": None}, """{"job": null}""", {"job": None}),
        ({"number": 187}, """{"number": 187}""", {"number": 187}),
        (
            {"nested": {"number": 187}},
            """{"nested": {"number": 187}}""",
            {"nested": {"number": 187}},
        ),
        # truncates long raw bodies
        ({"val": "a" * 20000}, json.dumps({"val": "a" * 20000}), {"val": "a" * 20000}),
        # Validate long raw bodies under the limit runs correctly
        ({"val": "a" * 1500}, json.dumps({"val": "a" * 1500}), {"val": "a" * 1500}),
    ],
)
def test_log_request_body(  # noqa: PLR0913
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
    data: Any,
    expected_request_body_raw: Any,
    expected_request_body: Any,
) -> None:
    caplog.set_level(logging.INFO)

    # send complex objects as json
    if isinstance(data, collections.abc.Mapping):
        client.post("/car", json=data, headers=TEST_AUTH_HEADERS)
    else:
        client.post("/car", data=data, headers=TEST_AUTH_HEADERS)

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record
    assert log_request_record.request_body_raw == expected_request_body_raw
    assert log_request_record.request_body == expected_request_body


@pytest.mark.parametrize(
    "mess_things_up",
    [patch("starlette.requests.Request.body", return_value=None)],
)
def test_log_request_is_resilient(
    client: TestClient,
    caplog: LogCaptureFixture,
    mess_things_up: ContextManager,  # type: ignore
    enable_route_logger_caplog: None,
) -> None:
    caplog.set_level(logging.INFO)

    with mess_things_up:
        client.post("/post", headers=TEST_AUTH_HEADERS)

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record


def test_log_response_body(
    client: TestClient,
    caplog: LogCaptureFixture,
    enable_route_logger_caplog: None,
) -> None:
    caplog.set_level(logging.INFO)
    with patch("todo_name_service.middleware.request_logger._is_health_check", return_value=False):
        response = client.get("/")

    log_request_record = find(lambda r: "Logging request/response" in r.message, caplog.records)
    assert log_request_record.response_body == response.json()
