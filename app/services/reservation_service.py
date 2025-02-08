from typing import Dict, Union

from fastapi import Depends
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.settings import get_db
from app.models.reservation import Reservation as ReservationModel
from app.models.room import Room
from app.schemas.reservations import (
    RerservationCreateRequest,
    RerservationCreateResponse,
)


def is_reservation_valid(
    reservation_data: RerservationCreateRequest, db: Session = Depends(get_db)
) -> Union[RerservationCreateRequest, Dict[str, str]]:
    if not reservation_data.start_time < reservation_data.end_time:
        logger.error("datetime not valid, start_time should be lower than end_time.")
        return False

    room = db.get(Room, reservation_data.room_id)
    if not room:
        logger.error("room does not exists.")
        return False

    if not room.capacity:
        logger.error("room capacity is already full.")
        return False

    already_reserved = (  # TODO - validar logica
        db.query(ReservationModel)
        .filter(  # TODO - generalizar logica  pq ja eh utilziada em outro lugar
            or_(
                and_(
                    ReservationModel.start_time < reservation_data.end_time,
                    ReservationModel.end_time > reservation_data.start_time,
                ),
                or_(
                    ReservationModel.start_time == reservation_data.start_time,
                    ReservationModel.end_time == reservation_data.end_time,
                ),
            ),
            ReservationModel.room_id == reservation_data.room_id,
        )
        .first()
    )

    if already_reserved:
        logger.error("room already reserved for this date.")
        return False

    return True


async def make_reservation(
    reservation_data: RerservationCreateRequest, db: Session = Depends(get_db)
) -> Union[RerservationCreateResponse, Dict[str, str]]:
    new_reservation = ReservationModel(**reservation_data.model_dump())

    room = db.get(Room, reservation_data.room_id)

    if (
        not room
    ):  # TODO - colocar logica em um lugar q de p reutilizar (no modelo? ou no utils?)
        logger.error("room does not exist.")
        return {"error": "room does not exist."}
    if not room.capacity:
        logger.error("room capacity is already full.")
        return {"error": "room capacity is already full."}

    room.capacity -= 1

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)

    logger.info("room reserved successfully.")

    return RerservationCreateResponse(**new_reservation.__dict__)


async def cancel_reservation(
    reservation_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    reservation = db.get(ReservationModel, reservation_id)

    if not reservation:
        return {"message": "reservation not found"}

    room = db.get(Room, reservation.room_id)
    room.capacity += 1
    db.delete(reservation)
    db.commit()

    logger.info("reservation cancelled successfully.")
    return {"message": "reservation cancelled successfully."}
