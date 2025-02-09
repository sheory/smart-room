from datetime import datetime, timezone
from typing import Dict, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core import constants
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
) -> bool:
    try:
        if reservation_data.start_time >= reservation_data.end_time:
            logger.error(constants.INVALID_DATETIME)
            raise HTTPException(status_code=400, detail=constants.INVALID_DATETIME)

        if reservation_data.start_time <= datetime.now(timezone.utc):
            logger.error(constants.INVALID_DATETIME_NOW)
            raise HTTPException(status_code=400, detail=constants.INVALID_DATETIME_NOW)

        room = db.get(Room, reservation_data.room_id)
        if not room:
            logger.error(constants.ROOM_DONT_EXISTS)
            raise HTTPException(status_code=400, detail=constants.ROOM_DONT_EXISTS)

        if not room.capacity:
            logger.error(constants.ROOM_CAPACITY_FULL)
            raise HTTPException(status_code=400, detail=constants.ROOM_CAPACITY_FULL)

        already_reserved = room_already_reserved_query(
            reservation_data.start_time,
            reservation_data.end_time,
            reservation_data.room_id,
            db,
        )

        if already_reserved:
            logger.error(constants.ROOM_ALREADY_RESERVERD)
            raise HTTPException(
                status_code=400, detail=constants.ROOM_ALREADY_RESERVERD
            )

        return True
    except Exception as e:
        logger.error(f"{constants.ERROR_VALIDATING_RESERVATION}: {str(e)}")
        raise HTTPException(
            status_code=(
                e.status_code
                if isinstance(e, HTTPException)
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=e.detail or str(e),
        )


async def make_reservation(
    reservation_data: RerservationCreateRequest, db: Session = Depends(get_db)
) -> Union[RerservationCreateResponse, Dict[str, str]]:
    try:
        new_reservation = ReservationModel(**reservation_data.model_dump())

        room = db.get(Room, reservation_data.room_id)

        if not room:
            logger.error(constants.ROOM_DONT_EXISTS)
            return {"error": constants.ROOM_DONT_EXISTS}
        if not room.capacity:
            logger.error(constants.ROOM_CAPACITY_FULL)
            return {"error": constants.ROOM_CAPACITY_FULL}

        room.capacity -= 1

        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)

        logger.info(constants.ROOM_RESERVED_SUCCESSFULLY)

        return RerservationCreateResponse(**new_reservation.__dict__)
    except Exception as e:
        logger.error(f"{constants.ERROR_MAKING_RESERVATION}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_MAKING_RESERVATION,
        )


async def cancel_reservation(
    reservation_id: int, username: str, db: Session = Depends(get_db)
) -> Dict[str, str]:
    try:
        reservation = db.get(ReservationModel, reservation_id)

        if not reservation:
            return {"message": constants.RESERVATION_NOT_FOUND}

        if reservation.user_name != username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=constants.NOT_AUTHORIZED_TO_CANCEL_RESERVATION,
            )

        room = db.get(Room, reservation.room_id)
        room.capacity += 1
        db.delete(reservation)
        db.commit()

        logger.info(constants.RESERVATION_CANCELLED_SUCCESSFULLY)
        return {"message": constants.RESERVATION_CANCELLED_SUCCESSFULLY}
    except Exception as e:
        logger.error(f"{constants.ERROR_CANCELLING_RESERVATION}: {str(e)}")
        raise HTTPException(
            status_code=(
                e.status_code
                if isinstance(e, HTTPException)
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=e.detail or str(e),
        )


def room_already_reserved_query(
    start_time: datetime,
    end_time: datetime,
    room_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(ReservationModel)
        .filter(
            and_(
                start_time < ReservationModel.end_time,
                end_time > ReservationModel.start_time,
            ),
            ReservationModel.room_id == room_id,
        )
        .first()
    )
