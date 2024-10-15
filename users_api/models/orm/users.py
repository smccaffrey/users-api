from sqlalchemy import Column, String

from users_api.models.base import Base  # type: ignore

# `id` uuid DEFAULT gen_random_uuid(),
# `username` text DEFAULT NULL,
# `name` text DEFAULT NULL,
# `email` text DEFAULT NULL,
# `sms` text DEFAULT NULL,
# `created` timestamptz DEFAULT now(),
# `lastseen` timestamptz DEFAULT NULL

class UsersORM(Base):
    __tablename__ = "users"

    username = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    sms = Column(String, nullable=True)

    # def __repr__(self):
    #     return f"<User {self.name} :: {self.email}>"
