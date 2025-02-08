from datetime import  date, datetime
from typing import List, Optional
from pydantic import BaseModel


class Room(BaseModel):
    name: str
    capacity: int
    location: str


class RoomGetResponse(Room):
    id: int


class RoomGetAllResponse(BaseModel):
    rooms: List[RoomGetResponse]


class RoomCreateRequest(Room):
    ...


class RoomCreateResponse(RoomGetResponse):
    ...


class RoomCheckAvailabilityRequest(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime


class RoomBookRequest(RoomCheckAvailabilityRequest):
    ...



class RoomGetReservationsRequest(BaseModel):
    room_id: str
    date: Optional[date]