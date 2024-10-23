from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from users_api.models.base import Base  # type: ignore
from users_api.models.orm.users_and_posts import users_and_posts


class PostsORM(Base):
    __tablename__ = "posts"

    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    content = Column(String, nullable=True)

    users = relationship(
        "UsersORM",
        secondary=users_and_posts,
        back_populates="posts"
    )
    