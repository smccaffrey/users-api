import enum
from abc import ABC
from typing import Union, Any
from http import HTTPStatus

from fastapi import HTTPException


class APIErrorMessage(enum.Enum):
    BAD_REQUEST = "BAD_REQUEST"
    NETWORK_ERROR = (
        "Uh oh, something unexpected happened."
        " We are trying to fix this as quickly as possible, so please try again later."
    )
    CLIENT_ERROR = (
        "Uh oh, looks like we're having trouble getting you connected."
        " Please try again later."
    )
    CONNECTION_RATE_LIMITED = "Uh oh, looks like we're having trouble getting you connected. Please try again later."
    INVALID_LINK_TOKEN_SIGNATURE = "Link token signature is invalid."  # nosec B105
    INVALID_LINK_TOKEN = "Link token is invalid."  # nosec B105
    EXPIRED_LINK_TOKEN = "Link token is expired."  # nosec B105
    STEP_RESULT_NOT_FOUND = "Step result not found for current job"
    INVALID_PLATFORM = "Platform not supported for offline DDS"


class APIErrorType(enum.Enum):
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    INVALID_REQUEST_PARAMETERS = "INVALID_REQUEST_PARAMETERS"
    UNAUTHORIZED_REQUEST = "UNAUTHORIZED_REQUEST"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class APIErrorCode(enum.Enum):
    UNKNOWN_ERROR = "UNKNOWN_ERROR", APIErrorType.UNKNOWN_ERROR
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND", APIErrorType.RECORD_NOT_FOUND
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED", APIErrorType.INVALID_REQUEST_PARAMETERS

    INVALID_PARAMS = "INVALID_PARAMS", APIErrorType.INVALID_REQUEST_PARAMETERS
    INVALID_REQUEST_BODY = (
        "INVALID_REQUEST_BODY",
        APIErrorType.INVALID_REQUEST_PARAMETERS,
    )
    INVALID_REQUEST_SIGNATURE = (
        "INVALID_REQUEST_SIGNATURE",
        APIErrorType.UNAUTHORIZED_REQUEST,
    )
    MISSING_FIELDS = "MISSING_FIELDS", APIErrorType.INVALID_REQUEST_PARAMETERS

    def __new__(cls, value: str, error_type: APIErrorType):
        obj = object.__new__(cls)
        obj._value_ = value
        # obj.error_type = error_type
        return obj


class UsersHTTPException(ABC, HTTPException):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(self, message: str, error_code: APIErrorCode, *args, **kwargs) -> None:
        self.message = message
        self.error_code = error_code
        # self.error_type = error_code.error_type.value
        super().__init__(*args, **kwargs)


class InvalidRequestParamsException(UsersHTTPException):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(
        self,
        error_code: APIErrorCode,
        message: Union[str, APIErrorMessage] = "Invalid Request.",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        error_message = (
            message.value if isinstance(message, APIErrorMessage) else message
        )
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            # message=error_message,
            # error_code=error_code,
            *args,
            **kwargs,
        )


class UnauthorizedRequestException(UsersHTTPException):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(
        self,
        error_code: APIErrorCode,
        message: Union[str, APIErrorMessage] = "Unauthorized Request",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        error_message = (
            message.value if isinstance(message, APIErrorMessage) else message
        )
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            # message=error_message,
            headers={"WWW-Authenticate": error_message},
            # error_code=error_code,
            *args,
            **kwargs,
        )


class UnknownErrorException(UsersHTTPException):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(
        self,
        error_code: APIErrorCode,
        message: Union[
            str, APIErrorMessage
        ] = "An unknown error occurred. Please try again later.",
        status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        error_message = (
            message.value if isinstance(message, APIErrorMessage) else message
        )
        super().__init__(
            status_code=status_code,
            # message=error_message,
            # error_code=error_code,
            *args,
            **kwargs,
        )


class ItemNotFoundException(UsersHTTPException):
    # pylint: disable=keyword-arg-before-vararg
    def __init__(
        self,
        error_code: APIErrorCode,
        message: str = "Item not found.",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            # message=message,
            # error_code=error_code,
            *args,
            **kwargs,
        )
