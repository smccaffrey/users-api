from typing import List
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session
from users_api.api.deps.db import get_db

from users_api.api.router import UsersRouter
from users_api.models.orm.posts import PostsORM
from users_api.models.posts import Post
from users_api.schemas.helpers import post_response
from users_api.schemas.posts import CreatePostRequest, PostsResponse, UpdatePostRequest
from users_api.managers.posts import posts_manager


posts_router = UsersRouter()

@posts_router.get("/")
def get_posts(
    db: Session = Depends(get_db)
) -> PostsResponse:

    posts: List[PostsORM] = posts_manager.get_all_posts(db)
    
    response_posts: List[Post] = [
        post_response(
            post=post
        )
        for post in posts
    ]
    
    return PostsResponse(posts=response_posts)


@posts_router.post("/")
def create_post(post_in: CreatePostRequest, db: Session = Depends(get_db)):

    created_post: PostsORM = posts_manager.create_post(db, post_in)

    return post_response(
        post=created_post
    )

@posts_router.get("/{post_id}")
def get_post(
    post_id: UUID,
    db: Session = Depends(get_db)
) -> Post:
    post: PostsORM = posts_manager.get_post_by_id(
        db_session=db,
        post_id=post_id
    )
    return post_response(
        post=post
    )


@posts_router.put("/{post_id}")
def update_post(
    post_id: UUID, 
    post_in: UpdatePostRequest,
    db_session: Session = Depends(get_db)
) -> Post:
    
    updated_post: PostsORM = posts_manager.update_post(
        db_session=db_session,
        post_id=post_id,
        obj_in=post_in
    )
    return post_response(
        post=updated_post
    )


@posts_router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: str,
    db_session: Session = Depends(get_db)
):
    return posts_manager.delete_post(db_session, post_id)
