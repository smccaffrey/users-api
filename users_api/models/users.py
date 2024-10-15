from typing import Optional
from pydantic import BaseModel

from uuid import UUID
import datetime

class User(BaseModel):
    id: Optional[UUID]
    username: Optional[str]
    name: Optional[str]
    email: Optional[str]
    sms: Optional[str]
    created_at: Optional[datetime.datetime]
    last_updated: Optional[datetime.datetime]
    

    model_config = {
        "from_attributes": True  # This is the new setting to replace orm_mode
    }

