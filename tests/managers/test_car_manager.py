from sqlalchemy.orm import Session

from todo_name_service.enums import CarColor
from todo_name_service.managers.car import car_manager
from todo_name_service.models.orm.car import Car
from todo_name_service.schemas.car import CarCreateRequest


# TODO: Replace this manager with your actual manager
def test_create(db_session: Session) -> None:
    cars = Car.query(db_session).all()
    assert len(cars) == 0

    car_manager.create(
        db_session=db_session,
        obj_in=CarCreateRequest(
            brand="ford",
            color=CarColor.RED,
            is_preowned=True,
        ),
    )

    cars = Car.query(db_session).all()
    assert len(cars) == 1

    assert cars[0].brand == "ford"
    assert cars[0].color == CarColor.RED
    assert cars[0].is_preowned is True
