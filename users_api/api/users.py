from uuid import UUID
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from users_api.api.deps.db import get_db
from users_api.api.router import UsersRouter
from users_api.models.users import User
from users_api.schemas.users import CreateUsersRequest, DeleteUserResponse
from users_api.schemas.users import UsersResponse

from users_api.managers.users import users_manager
from users_api.models.orm.users import UsersORM

users_router = UsersRouter()


@users_router.get("/")
async def get_users(db_session: Session = Depends(get_db)) -> UsersResponse:
    try:
        users = users_manager.get_multi(db_session=db_session)

        return UsersResponse(users=[User.model_validate(user) for user in users])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@users_router.get("/{user_id}")
async def get_user(
    user_id: UUID, db_session: Session = Depends(get_db)
) -> UsersResponse:
    try:
        user = users_manager.get(db_session=db_session, id=user_id)

        return UsersResponse(users=[User.model_validate(user)])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@users_router.post("/")
async def post_user(
    request: CreateUsersRequest, db_session: Session = Depends(get_db)
) -> UsersResponse:
    try:

        user: UsersORM = users_manager.create_or_update(
            db_session=db_session, obj_in=request
        )
        print(User.model_validate(user))
        return UsersResponse(users=[User.model_validate(user)])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID, db_session: Session = Depends(get_db)
) -> DeleteUserResponse:
    try:
        user = users_manager.get(db_session=db_session, id=user_id)

        db_session.delete(user)
        db_session.commit()

        return DeleteUserResponse(status=f"Successfully deleted user: {user_id}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
