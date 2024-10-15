from typing import List, Optional
from pydantic import BaseModel

from users_api.models.users import User


class UsersRequest(BaseModel):
    user: User


class UsersResponse(BaseModel):
    users: List[User]


class CreateUsersRequest(BaseModel):
    email: Optional[str]
    sms: Optional[str]

class DeleteUserResponse(BaseModel):
    status: str