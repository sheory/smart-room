from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core import constants
from app.core.logger import logger
from app.db.settings import get_db
from app.models.reservation import Reservation
from app.models.room import Room as RoomModel
from app.schemas.reservations import ReservationGetAllResponse
from app.schemas.rooms import (
    RoomCheckAvailabilityRequest,
    RoomCreateRequest,
    RoomCreateResponse,
    RoomGetAllResponse,
)


async def create_room(
    room_data: RoomCreateRequest, db: Session = Depends(get_db)
) -> RoomCreateResponse:
    try:
        new_room = RoomModel(**room_data.model_dump())

        db.add(new_room)
        db.commit()
        db.refresh(new_room)

        logger.info(f"{constants.ROOM_CREATED_SUCCESSFULLY}: {new_room.name}.")

        return RoomCreateResponse(**new_room.__dict__)
    except Exception as e:
        logger.error(f"{constants.ERROR_CREATING_ROOM}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_CREATING_ROOM,
        )


async def get_rooms(
    limit: int, offset: int, db: Session = Depends(get_db)
) -> RoomGetAllResponse:
    try:
        all_rooms: RoomModel = db.query(RoomModel).offset(offset).limit(limit).all()

        rooms = []
        for room in all_rooms:
            rooms.append(room.__dict__)

        logger.info(
            f"Got {len(rooms)} rooms successfully with pagination:"
            f"limit={limit}, offset={offset}."
        )

        return RoomGetAllResponse(rooms=rooms)
    except Exception as e:
        logger.error(f"{constants.ERROR_GETTING_ROOMS}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_GETTING_ROOMS,
        )


async def get_reservations(
    room_id: int, limit: int, offset: int, db: Session = Depends(get_db)
) -> ReservationGetAllResponse:
    try:
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
    except Exception as e:
        logger.error(
            f"{constants.ERROR_GETTING_RESERVATIONS} for room {room_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_GETTING_RESERVATIONS,
        )


async def check_availability(
    params: RoomCheckAvailabilityRequest, db: Session = Depends(get_db)
) -> bool:
    try:
        any_room: RoomModel = (
            db.query(RoomModel)
            .join(Reservation, Reservation.room_id == RoomModel.id)
            .filter(  # TODO - check and generalize this filter
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

        if any_room:
            logger.error(constants.ROOM_ALREADY_RESERVERD)
            return False

        logger.info(f"Room {params.id} available.")
        return True
    except Exception as e:
        logger.error(f"{constants.ERROR_CHECKING_ROOM} {params.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_CHECKING_ROOM,
        )
