from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class RerservationCreateRequest(BaseModel):
    room_id: int
    user_name: str
    start_time: datetime
    end_time: datetime


class RerservationCreateResponse(RerservationCreateRequest):
    id: int


class RoomGetReservationsRequest(BaseModel):
    room_id: int
    date: Optional[date]


class ReservationGetAllResponse(BaseModel):
    reservations: List[RerservationCreateResponse]
