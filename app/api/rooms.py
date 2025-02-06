from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.settings import get_db
from app.schemas.rooms import RoomBookRequest, RoomCheckAvailabilityRequest, RoomCreateRequest, RoomGetReservationsRequest, RoomGetResponse
from app.services.room_service import create_room


room_router = APIRouter()

@room_router.get(
    "/",
    description="Get all rooms"
)
async def get_rooms() -> RoomGetResponse:
    ...


@room_router.post(
    "/",
    description="Create a room"
)
async def create(room_data: RoomCreateRequest, db: Session = Depends(get_db)) -> RoomGetResponse:
    response = create_room(room_data)

    return response


@room_router.get(
    "/availability",
    description="Check room availability"
)
async def check_availability(room_data: RoomCheckAvailabilityRequest): #TODO - typing
    ...


@room_router.post(
    "/reservations",
    description="Book a room"
)
async def book_room(room_data: RoomBookRequest): #TODO - typing
    ...


@room_router.delete(
    "/reservations/{id}",
    description="Cancel a room book"
)
async def unbook_room(room_id: int): #TODO - typing
    ...


@room_router.get(
    "/reservations/{id}",
    description="Get room reservations"
)
async def get_room_reservations(room_data: RoomGetReservationsRequest) -> RoomGetResponse:
    ...
