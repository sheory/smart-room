from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.settings import get_db
from app.schemas.reservations import (
    RerservationCreateRequest,
    RerservationCreateResponse,
)
from app.services.reservation_service import (
    cancel_reservation,
    is_reservation_valid,
    make_reservation,
)

reservation_router = APIRouter()


@reservation_router.post("/", description="Make a room reservation")
async def make_room_reservation(
    reservation_data: RerservationCreateRequest, db: Session = Depends(get_db)
) -> Union[RerservationCreateResponse, Dict[str, str]]:
    valid_reservation = is_reservation_valid(
        reservation_data=reservation_data,
        db=db
    )
    if not valid_reservation:
        return {"error": "Not a valid reservation"}

    response = await make_reservation(reservation_data=reservation_data, db=db)

    return response


@reservation_router.delete(
    "/{reservation_id}",
    description="Cancel a room book"
)
async def cancel_room_reservation(
    reservation_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    response = await cancel_reservation(reservation_id, db)

    return response
