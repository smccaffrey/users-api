import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from users_api.api.deps.db import get_db
from users_api.app import app
from users_api.models.orm.posts import PostsORM
from users_api.models.orm.users import UsersORM
from users_api.schemas.posts import CreatePostRequest

TEST_AUTH_HEADERS = {"Authorization": "Bearer test_token"}


# Mock database dependency
def override_get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_get_posts(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    request_body = {
        "title": "Test Post",
        "description": "A description for the new post",
        "content": "This is the content of the new post",
        "user_id": str(user_id),
    }

    client.post("/posts/", headers=TEST_AUTH_HEADERS, json=request_body)

    response = client.get("/posts/", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) > 0
    assert data["posts"][0]["title"] == "Test Post"


def test_create_post(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    request_body = {
        "title": "New Post",
        "description": "A description for the new post",
        "content": "This is the content of the new post",
        "user_id": str(user_id),
    }

    response = client.post("/posts/", headers=TEST_AUTH_HEADERS, json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == request_body["title"]


def test_get_post(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    request_body = {
        "title": "Specific Post",
        "description": "A description for the new post",
        "content": "This is the content of the new post",
        "user_id": str(user_id),
    }

    test_post = client.post(
        "/posts/", headers=TEST_AUTH_HEADERS, json=request_body
    ).json()

    post_id = test_post["id"]
    response = client.get(f"/posts/{post_id}", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(post_id)
    assert data["title"] == "Specific Post"


def test_update_post(client: TestClient, db_session: Session) -> None:
    user_id = uuid.uuid4()
    db_session.add(UsersORM(id=user_id, name="Test User", email="test@example.com"))
    db_session.commit()

    request_body = {
        "title": "Specific Post",
        "description": "A description for the new post",
        "content": "This is the content of the new post",
        "user_id": str(user_id),
    }

    test_post = client.post(
        "/posts/", headers=TEST_AUTH_HEADERS, json=request_body
    ).json()

    post_id = test_post["id"]

    update_data = {
        "title": "Updated Post Title",
        "content": "Updated content",
        "user_id": str(user_id),
    }

    response = client.put(
        f"/posts/{post_id}", headers=TEST_AUTH_HEADERS, json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Post Title"
    assert data["content"] == "Updated content"


def test_delete_post(client: TestClient, db_session: Session) -> None:
    post_id = uuid.uuid4()
    db_session.add(
        PostsORM(
            id=post_id,
            title="Post to Delete",
            description="Description of post to delete",
            content="Content of post to delete",
        )
    )
    db_session.commit()

    response = client.delete(f"/posts/{post_id}", headers=TEST_AUTH_HEADERS)
    assert response.status_code == 204
