# from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Table, Column, ForeignKey
from users_api.models.base import Base

users_and_posts = Table(
    "users_and_posts",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True)
)
