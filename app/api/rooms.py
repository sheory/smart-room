from typing import Dict, Union
from app.core import constants
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.settings import get_db
from app.schemas.reservations import ReservationGetAllResponse
from app.schemas.rooms import (
    RoomCheckAvailabilityRequest,
    RoomCreateRequest,
    RoomCreateResponse,
    RoomGetAllResponse,
)
from app.services.room_service import (
    check_availability,
    create_room,
    get_reservations,
    get_rooms,
)

room_router = APIRouter()


@room_router.post("/", description="Create a room")
async def create(
    room_data: RoomCreateRequest, db: Session = Depends(get_db)
) -> Union[RoomCreateResponse, HTTPException]:
    try:
        response = await create_room(room_data, db)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.INTERNAL_SERVER_ERROR,
        )


@room_router.get("/", description="Get all rooms")
async def get_all(
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Union[RoomGetAllResponse, HTTPException]:
    try:
        response = await get_rooms(db=db, limit=limit, offset=offset)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.INTERNAL_SERVER_ERROR,
        )


@room_router.get("/{room_id}/reservations", description="Get room reservations")
async def get_room_reservations(
    room_id: int,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> Union[ReservationGetAllResponse, HTTPException]:
    try:
        response = await get_reservations(
            limit=limit, offset=offset, room_id=room_id, db=db
        )
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.INTERNAL_SERVER_ERROR,
        )


@room_router.get("/{id}/availability", description="Check room availability")
async def check_room_availability(
    id: int,
    start_time: str = Query(...),
    end_time: str = Query(...),
    db: Session = Depends(get_db),
) -> Union[Dict[str, str], HTTPException]:
    try:
        room_params = RoomCheckAvailabilityRequest(
            id=id, start_time=start_time, end_time=end_time
        )
        is_available = await check_availability(room_params, db)

        availability = "available" if is_available else "unavailable"
        return {"message": f"Room is {availability}"}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=constants.INTERNAL_SERVER_ERROR,
        )
