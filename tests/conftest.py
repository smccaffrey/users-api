import logging

from typing import Any, Generator

import pytest

from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture
from embassy.enums import InternalPinwheelSubject
from embassy.fastapi.exceptions import UnauthorizedRequest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.requests import Request

import alembic

from alembic.config import Config
from todo_name_service import settings
from todo_name_service.api.deps.db import get_db
from todo_name_service.api.routes import _M2M_AUTHORIZER
from todo_name_service.app import app as app_instance


# Add any fixture filepaths here
pytest_plugins = ["tests.fixtures.factories"]

engine = create_engine(settings.DATABASE_URL)

TEST_AUTH_HEADERS = {"authorization": "Bearer eyjwt.sdfdsf.abcd"}


@pytest.fixture(scope="session", autouse=True)
def app() -> Generator[FastAPI, None, None]:
    """
    Create a fresh database for the test session.
    """
    # Use Alembic to mirror production DB creation
    alembic_config = Config()
    alembic_config.set_main_option("script_location", str(settings.REPO_ROOT / "alembic"))
    alembic_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    alembic.command.upgrade(alembic_config, "head")
    yield app_instance
    # Doesn't use Alembic downgrade since many downgrades are broken (PP-5054)
    with engine.connect() as conn:
        tables = conn.execute("SELECT tablename FROM pg_tables WHERE schemaname IN ('public');")
        for (table,) in tables:
            conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")


@pytest.fixture(autouse=True)
def db_session(request: FixtureRequest, caplog: LogCaptureFixture) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """
    capture_db_logs = request.node.get_closest_marker("capture_db_logs")
    if capture_db_logs:
        # must enable logging before the SQLAlchemy connection is created
        # https://docs.sqlalchemy.org/en/13/core/engines.html#configuring-logging
        caplog.set_level(logging.INFO, "sqlalchemy.engine")
    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)
    yield session  # use the session in tests.
    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()  # type: ignore
    # return connection to the Engine
    connection.close()


def mock_authorizer(
    authorization: str = Header(default="", description="Fake JWT Bearer Auth")
) -> InternalPinwheelSubject:
    if authorization == TEST_AUTH_HEADERS["authorization"]:
        return InternalPinwheelSubject.NEWTON
    raise UnauthorizedRequest()


@pytest.fixture()
def client(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into api.
    """

    def _get_test_db(request: Request) -> Generator[Session, None, None]:
        request.state.db_session = db_session
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[_M2M_AUTHORIZER.authorize_request] = mock_authorizer

    with TestClient(app) as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture()
def client_no_exceptions(app: FastAPI, db_session: Session) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into api.

    Different from the client() fixture in that it doesn't raise exceptions
    """

    def _get_test_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[_M2M_AUTHORIZER.authorize_request] = mock_authorizer

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides = {}
