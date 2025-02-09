from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import constants
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


@reservation_router.post(
    "/",
    description="Make a room reservation",
    response_model=RerservationCreateResponse,
)
async def make_room_reservation(
    reservation_data: RerservationCreateRequest, db: Session = Depends(get_db)
) -> RerservationCreateResponse:
    try:
        if not is_reservation_valid(reservation_data=reservation_data, db=db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=constants.INVALID_RESERVATION,
            )

        response = await make_reservation(reservation_data=reservation_data, db=db)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.detail or str(e),
        )


@reservation_router.delete(
    "/{reservation_id}", description="Cancel a room reservation", response_model=dict
)
async def cancel_room_reservation(
    reservation_id: int, db: Session = Depends(get_db)
) -> dict:
    try:
        return await cancel_reservation(reservation_id, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.ERROR_CANCELLING_RESERVATION,
        )
