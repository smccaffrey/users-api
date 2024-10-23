from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from users_api.managers.base import BaseManager

from users_api.models.orm.posts import PostsORM
from users_api.models.orm.users import UsersORM
from users_api.schemas.posts import (
    CreatePostRequest,
    DeletePostResponse,
    UpdatePostRequest,
)
from fastapi import HTTPException, status


class PostsManager(BaseManager[PostsORM]):

    def get_all_posts(self, db_session: Session):
        return (
            db_session.query(self.model)
            .join(self.model.users)  # Join the users through the relationship
            .options(
                joinedload(self.model.users)
            )  # Eager load the related users, solves N+1 problem
            .all()
        )

    def create_post(self, db_session: Session, obj_in: CreatePostRequest) -> PostsORM:
        # Check if the user_id exists
        user = db_session.query(UsersORM).filter_by(id=obj_in.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id"
            )

        # Create a new post
        db_post = self.model(
            title=obj_in.title,
            content=obj_in.content,
            # user_id=obj_in.user_id,
        )

        # update mapping
        user.posts.append(db_post)

        db_session.add(db_post)
        db_session.commit()
        db_session.refresh(db_post)
        return db_post

    def get_post_by_id(self, db_session: Session, post_id: UUID) -> PostsORM:
        db_post = (
            db_session.query(self.model)
            .filter_by(id=post_id)
            .join(self.model.users)  # Join the users through the relationship
            .options(
                joinedload(self.model.users)
            )  # Eager load the related users, solves N+1 problem
            .first()
        )
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )
        return db_post

    def update_post(
        self, db_session: Session, post_id: UUID, obj_in: UpdatePostRequest
    ) -> PostsORM:
        # Fetch the post by ID
        db_post = (
            db_session.query(self.model)
            .filter_by(id=post_id)
            .join(self.model.users)  # Join the users through the relationship
            .options(
                joinedload(self.model.users)
            )  # Eager load the related users, solves N+1 problem
            .first()
        )
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        # Validate user_id
        user = db_session.query(UsersORM).filter_by(id=obj_in.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id"
            )

        # Update the post details
        db_post.title = obj_in.title
        db_post.content = obj_in.content
        db_post.user_id = obj_in.user_id

        db_session.commit()
        db_session.refresh(db_post)
        return db_post

    def delete_post(self, db_session: Session, post_id: str) -> DeletePostResponse:
        db_post: PostsORM = db_session.query(self.model).filter_by(id=post_id).first()

        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
            )

        db_session.delete(db_post)
        db_session.commit()
        return DeletePostResponse(
            status="Post deleted successfully", code=status.HTTP_204_NO_CONTENT
        )


posts_manager = PostsManager(PostsORM)
