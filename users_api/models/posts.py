import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from users_api.models.users import User


class Post(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    content: Optional[str]
    created_at: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]

    user: User

    model_config = {"from_attributes": True}
