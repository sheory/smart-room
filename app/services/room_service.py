from app.schemas.rooms import Room, RoomCreateRequest, RoomGetResponse, RoomGetAllResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.settings import get_db
from app.models.room import Room as RoomModel

async def create_room(room_data: RoomCreateRequest, db: Session = Depends(get_db)) -> RoomGetResponse:
    new_room = Room(**room_data.model_dump())

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    #log created succesfully

    return RoomGetResponse(new_room)


async def get_rooms(db: Session = Depends(get_db)) -> RoomGetAllResponse:

    all: RoomModel = db.query(RoomModel)

    #log got succesfully
    print(all)
    rooms_dict = []
    for room in all:
        rooms_dict.append(room._asdict())
    return RoomGetAllResponse(all)