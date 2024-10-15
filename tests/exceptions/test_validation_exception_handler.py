import json

from http import HTTPStatus
from typing import Any

import pytest

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError, validator
from starlette.requests import Request

from todo_name_service.api.exceptions import APIErrorCode, APIErrorType
from todo_name_service.exceptions.validation_exception_handler import (
    validation_exception_handler,
)


@pytest.fixture
def starlette_request() -> Request:
    request = Request({"type": "http", "method": "POST", "path": "/v1/link_tokens"})
    return request


@pytest.mark.asyncio
async def test_validation_exception_handler_root_level_field_validation_error(
    starlette_request: Request,
) -> None:
    """
    Validate that when a request is missing a required field at the root-level,
    we correctly translate to the INVALID_PARAMS error code and appropriate message.
    """

    class ValidationErrorModel(BaseModel):
        """Custom class to throw ValidationError for __root__ field"""

        __root__: str

        @validator("__root__")
        def __root___always_raise_error(cls, value: Any) -> None:  # noqa: N805
            raise ValueError("Default raise error")

    try:
        ValidationErrorModel(__root__="dummy")
    except ValidationError:
        request_validation_error = RequestValidationError(
            [{"loc": ("__root__",), "msg": "Default raise error", "type": "value_error"}]
        )

    json_response = await validation_exception_handler(starlette_request, request_validation_error)

    response_obj = json.loads(json_response.body)["error"]

    assert response_obj["code"] == APIErrorCode.INVALID_PARAMS.value
    assert response_obj["type"] == APIErrorType.INVALID_REQUEST_PARAMETERS.value
    assert response_obj["fields"][0]["name"] == "__root__"
    assert response_obj["fields"][0]["message"] == "Default raise error."
    assert response_obj["status_code"] == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_validation_exception_handler_missing_field(
    starlette_request: Request,
) -> None:
    """
    Validate that when a request is missing a required field in the body,
    we correctly translate to the MISSING_FIELDS error code and appropriate message.
    """

    class MissingFieldModel(BaseModel):
        """Custom class to throw ValidationError for field missing_field"""

        missing_field: str

    try:
        MissingFieldModel()
    except ValidationError:
        request_validation_error = RequestValidationError(
            [
                {
                    "loc": ("body", "missing_field"),
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        )

    json_response = await validation_exception_handler(starlette_request, request_validation_error)

    response_obj = json.loads(json_response.body)["error"]

    assert response_obj["code"] == APIErrorCode.MISSING_FIELDS.value
    assert response_obj["type"] == APIErrorType.INVALID_REQUEST_PARAMETERS.value
    assert response_obj["message"] == "Request is missing required fields: [missing_field]."
    assert response_obj["fields"][0]["name"] == "missing_field"
    assert response_obj["fields"][0]["message"] == "Field required."
    assert response_obj["status_code"] == HTTPStatus.BAD_REQUEST
