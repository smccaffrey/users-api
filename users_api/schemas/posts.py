from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from users_api.models.posts import Post


class PostsRequest(BaseModel):
    post: Post


class PostsResponse(BaseModel):
    posts: Optional[List[Post]] = None
    message: Optional[str] = None


class CreatePostRequest(BaseModel):
    title: str
    description: Optional[str]
    content: Optional[str]

    user_id: UUID


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: UUID


class DeletePostResponse(BaseModel):
    status: str
    code: int
