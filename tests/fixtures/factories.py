from typing import Iterator

import factory
import pytest

from shared_python.helper_functions import now
from sqlalchemy.orm import Session

from todo_name_service.enums import CarColor
from todo_name_service.models.orm.car import Car


class PinwheelFactory(factory.alchemy.SQLAlchemyModelFactory):
    # These get populated through the fixture "industry" below
    _default_link_token = None
    _default_api_key = None

    # Because all tests are wrapped in an outer transaction
    # they will all get the same database timestamps. We
    # have to set these manually.
    # https://stackoverflow.com/a/33532154
    created_at = factory.LazyFunction(now)
    updated_at = factory.LazyFunction(now)

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):  # type: ignore
        obj = super()._save(model_class, session, *args, **kwargs)
        session.refresh(obj)
        return obj

    class Meta:
        abstract = True


# TODO: Replace this example factory with your model
class CarFactory(PinwheelFactory):
    brand: str = "ford"
    color: CarColor = CarColor.RED
    is_preowned: bool = False

    class Meta:
        model = Car


class FactoryManager:
    def __init__(self, session: Session):
        self.session = session
        self.CarFactory = CarFactory

        for fac in self.factories():
            fac._meta.sqlalchemy_session = session
            fac._meta.sqlalchemy_session_persistence = "commit"

    def factories(self) -> Iterator[PinwheelFactory]:
        return (getattr(self, attr) for attr in vars(self) if attr.endswith("Factory"))


@pytest.fixture()
def industry(db_session: Session) -> FactoryManager:
    """
    Industry, home of factories.
    Credit: https://typenil.com/blog/sqlalchemy-session-wrapping-factories/

    Return a FactoryManager which holds references to all Factories to use.
    Each has been populated with a Session, LinkToken, and APIKey for use.
    """
    return FactoryManager(db_session)
