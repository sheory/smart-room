from fastapi import Depends
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.db.settings import get_db
from app.models.reservation import Reservation
from app.models.room import Room as RoomModel
from app.schemas.reservations import ReservationGetAllResponse
from app.schemas.rooms import (RoomCheckAvailabilityRequest, RoomCreateRequest,
                               RoomCreateResponse, RoomGetAllResponse)


async def create_room(
    room_data: RoomCreateRequest, db: Session = Depends(get_db)
) -> RoomCreateResponse:
    new_room = RoomModel(**room_data.model_dump())

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    logger.info(f"room {new_room.name} created successfully.")

    return RoomCreateResponse(**new_room.__dict__)


async def get_rooms(
    limit: int, offset: int, db: Session = Depends(get_db)
) -> RoomGetAllResponse:
    all_rooms: RoomModel = db.query(RoomModel).offset(offset).limit(limit).all()

    rooms = []
    for room in all_rooms:
        rooms.append(room.__dict__)

    logger.info(
        f"Got {len(rooms)} rooms successfully with pagination: limit={limit}, offset={offset}."
    )

    return RoomGetAllResponse(rooms=rooms)


async def get_reservations(
    room_id: int, limit: int, offset: int, db: Session = Depends(get_db)
) -> ReservationGetAllResponse:
    all_reservations: RoomModel = (
        db.query(Reservation)
        .join(RoomModel, Reservation.room_id == room_id)
        .offset(offset)
        .limit(limit)
    )

    reservations = []
    for reservation in all_reservations:
        reservations.append(reservation.__dict__)

    logger.info(f"Got all reservations for room {room_id} successfully.")
    return ReservationGetAllResponse(reservations=reservations)


async def check_availability(
    params: RoomCheckAvailabilityRequest, db: Session = Depends(get_db)
) -> bool:
    any_room: RoomModel = (
        db.query(RoomModel)
        .join(Reservation, Reservation.room_id == RoomModel.id)
        .filter(  # TODO -checar e generalizazr esse filtro
            or_(
                and_(
                    Reservation.start_time < params.end_time,
                    Reservation.end_time > params.start_time,
                ),
                or_(
                    Reservation.start_time == params.start_time,
                    Reservation.end_time == params.end_time,
                ),
            ),
            RoomModel.id == params.id,
        )
        .first()
    )

    if any_room:  # TODO- generalizar
        logger.error(
            "Room already reserved at this date and time."
        )  # TODO - criar constantes p log
        return False

    logger.info(f"room {params.id} available.")
    return True
