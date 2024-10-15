from uuid import uuid4

import pytest

from sqlalchemy.orm import Session
from sqlalchemy_mixins import ModelNotFoundError

from tests.fixtures.factories import FactoryManager
from todo_name_service.models.orm.base import Base, BaseQuery
from todo_name_service.models.orm.car import Car


class TestSQLAlchemyMixins:
    """Collection of tests related to the sqlalchemy-mixins package"""

    def test_sqlalchemy_mixins_basics(self, db_session: Session, industry: FactoryManager) -> None:
        """Assert sqlalchemy-mixins is hooked up properly."""
        car = industry.CarFactory()

        fresh_find = Car.query(db_session).find(car.id)
        assert fresh_find == car

        with pytest.raises(ModelNotFoundError):
            Car.query(db_session).find_or_fail(str(uuid4()))

    def test_query_cls_applied(self) -> None:
        for klass in Base.__subclasses__():
            if klass.__abstract__:
                continue

            query = klass.query
            assert isinstance(query, BaseQuery)
            assert isinstance(query, klass.query_cls)

    def test_query_where_if_not_none(self, db_session: Session, industry: FactoryManager) -> None:
        """Assert None filter value will not affect search results"""
        car = industry.CarFactory()

        found_api_key = Car.query(db_session).where_if_not_none(id=car.id).first()
        assert found_api_key == car
