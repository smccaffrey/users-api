# conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from users_api import settings
from users_api.app import app  # Adjust to your actual app import
from users_api.api.deps.db import get_db
from users_api.models.base import Base  # Your SQLAlchemy Base class

from sqlalchemy.orm import Session

# SQLALCHEMY_DATABASE_URL = "postgresql:///./test.db"
engine = create_engine(
    settings.TEST_DATABASE_URL,
)

# Create a sessionmaker for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the test database
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def db_session():
    """Fixture to create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()

    db = TestingSessionLocal(bind=connection)
    yield db

    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client(db_session: Session):
    """Fixture to create a TestClient for the FastAPI app with a mock DB session."""

    # Override the dependency to use the test DB session
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
