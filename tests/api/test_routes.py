import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from users_api.api.deps.db import get_db
from users_api.app import app  # Adjust the import according to your project structure
from users_api.models.orm.users import UsersORM
from users_api.schemas.users import CreateUsersRequest

# client = TestClient(app)

TEST_AUTH_HEADERS = {
    "Authorization": "Bearer test_token"
}  # Adjust as per your auth mechanism


# Mock database dependency
def override_get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_get_users(client: TestClient, db_session: Session) -> None:
    # Setup mock data in the db_session
    db_session.add(
        UsersORM(id=uuid.uuid4(), name="Test User", email="test@example.com")
    )
    db_session.commit()

    # Test the /users/ route
    response = client.get("/users/", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) > 0
    assert data["users"][0]["email"] == "test@example.com"


def test_get_user(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    # Setup mock data
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    response = client.get(f"/users/{user_id}", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["users"][0]["id"] == str(user_id)
    assert data["users"][0]["email"] == "test@example.com"


def test_post_user(client: TestClient, db_session: Session) -> None:
    # Prepare the request body
    request_body = {
        # "name": "New User",
        "email": "newuser@example.com",
        "sms": "1234567890",
    }

    # Test the /users/ POST route
    response = client.post("/users/", headers=TEST_AUTH_HEADERS, json=request_body)
    assert response.status_code == 200
    data = response.json()

    assert data["users"][0]["sms"] == "1234567890"
    assert data["users"][0]["email"] == "newuser@example.com"


def test_delete_user(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    # Setup mock data
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    # Test the /users/{user_id} DELETE route
    response = client.delete(f"/users/{user_id}", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == f"Successfully deleted user: {user_id}"
