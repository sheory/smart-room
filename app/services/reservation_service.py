from typing import Dict, Union

from app.core import constants
from fastapi import Depends, HTTPException, status
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
    try:
        if not reservation_data.start_time < reservation_data.end_time:
            logger.error(
                constants.INVALID_DATETIME
            )
            return False

        room = db.get(Room, reservation_data.room_id)
        if not room:
            logger.error(constants.ROOM_DONT_EXISTS)
            return False

        if not room.capacity:
            logger.error(constants.ROOM_CAPACITY_FULL)
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
            logger.error(constants.ROOM_ALREADY_RESERVERD)
            return False

        return True
    except Exception as e:
        logger.error(f"{constants.ERROR_VALIDATING_RESERVATION}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_VALIDATING_RESERVATION,
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
    reservation_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    try:
        reservation = db.get(ReservationModel, reservation_id)

        if not reservation:
            return {"message": constants.RESERVATION_NOT_FOUND}

        room = db.get(Room, reservation.room_id)
        room.capacity += 1
        db.delete(reservation)
        db.commit()

        logger.info(constants.RESERVATION_CANCELLED_SUCCESSFULLY)
        return {"message": constants.RESERVATION_CANCELLED_SUCCESSFULLY}
    except Exception as e:
        logger.error(f"{constants.ERROR_CANCELLING_RESERVATION}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_CANCELLING_RESERVATION,
        )
