from unittest import mock
from unittest.mock import MagicMock

from fastapi import FastAPI

from todo_name_service.services.sentry import init_sentry


@mock.patch("todo_name_service.services.sentry.init")
def test_sentry_initialized(mocked_init: MagicMock, app: FastAPI) -> None:
    mocked_init.assert_not_called()
    with mock.patch("todo_name_service.services.sentry.settings.IS_TEST", False), mock.patch(
        "todo_name_service.services.sentry.settings.SENTRY_DSN", "1234"
    ):
        init_sentry(app)
        mocked_init.assert_called()
