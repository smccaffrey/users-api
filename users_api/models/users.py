import datetime
from uuid import UUID

from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[UUID]
    username: Optional[str]
    name: Optional[str]
    email: Optional[str]
    sms: Optional[str]
    created_at: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]

    model_config = {"from_attributes": True}
