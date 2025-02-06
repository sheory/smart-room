from datetime import  date, datetime
from typing import List, Optional
from pydantic import BaseModel


class Room(BaseModel):
    name: str
    capacity: str
    location: str


class RoomGetResponse(Room):
    ...


class RoomGetAllResponse(BaseModel):
    rooms: List[Room]


class RoomCreateRequest(Room):
    ...


class RoomCheckAvailabilityRequest(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime


class RoomBookRequest(RoomCheckAvailabilityRequest):
    room_id: str


class RoomGetReservationsRequest(BaseModel):
    room_id: str
    date: Optional[date]