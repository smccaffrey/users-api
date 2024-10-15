from sqlalchemy.orm import Session

from users_api.managers.base import BaseManager
from users_api.models.orm.users import UsersORM

from users_api.schemas.users import CreateUsersRequest

class UsersManager(BaseManager[UsersORM]):

    def create_or_update(
        self,
        db_session: Session,
        obj_in: CreateUsersRequest
    ) -> UsersORM:

        db_obj = (
            db_session.query(self.model)
            .filter_by(email=obj_in.email)
            .first()  # type: ignore
        )

        if not db_obj:
            db_obj = (
                db_session.query(self.model)
                .filter_by(sms=obj_in.sms)
                .first()  # type: ignore
            )

        if db_obj:
            # db_obj.username = obj_in.user.username  # type: ignore
            # db_obj.name = obj_in.user.name  # type: ignore
            db_obj.email = obj_in.email  # type: ignore
            db_obj.sms = obj_in.sms  # type: ignore

        else:
            db_obj = self.model(
                # username = obj_in.user.username,
                # name = obj_in.user.name,
                email = obj_in.email,
                sms = obj_in.sms,
            )

        db_session.add(db_obj)
        db_session.commit()

        return db_obj


users_manager = UsersManager(UsersORM)
