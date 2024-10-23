from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from users_api.models.base import Base  # type: ignore
from users_api.models.orm.users_and_posts import users_and_posts


class UsersORM(Base):
    __tablename__ = "users"

    username = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    sms = Column(String, nullable=True)

    posts = relationship("PostsORM", secondary=users_and_posts, back_populates="users")
