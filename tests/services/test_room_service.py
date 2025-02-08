from datetime import datetime
from app.models.reservation import Reservation
from app.models.room import Room
from app.schemas.reservations import ReservationGetAllResponse
from app.schemas.rooms import RoomCheckAvailabilityRequest, RoomCreateRequest, RoomCreateResponse, RoomGetAllResponse
from app.services.room_service import check_availability, create_room, get_reservations, get_rooms
import pytest
from unittest.mock import MagicMock


"""@pytest.mark.asyncio
async def test_create_room():
    mock_db = MagicMock()

    room_data = RoomCreateRequest(name="Room 1", capacity=10, location="Andar 1")
    response = await create_room(room_data, mock_db)

    assert isinstance(response, RoomCreateResponse)
    assert response.name == "Room 1"
    assert response.capacity == 10

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
"""

@pytest.mark.asyncio
async def test_get_rooms():
    mock_db = MagicMock()

    mock_rooms = [
        Room(id=1, name="Room 1", capacity=10, location="Andar 1"),
        Room(id=2, name="Room 2", capacity=15, location="Andar 2")
    ]

    mock_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_rooms

    limit = 2
    offset = 0
    response = await get_rooms(limit, offset, mock_db)

    assert isinstance(response, RoomGetAllResponse)

    assert len(response.rooms) == 2
    assert response.rooms[0].name == "Room 1"
    assert response.rooms[1].name == "Room 2"

    mock_db.query.return_value.offset.return_value.limit.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_reservations():
    mock_db = MagicMock()

    mock_reservations = [
        Reservation(id=1, room_id=1, user_name="name 1", start_time="2025-02-01T00:00:00", end_time="2025-02-01T01:00:00"),
        Reservation(id=2, room_id=1, user_name="name 2", start_time="2025-02-02T00:00:00", end_time="2025-02-02T01:00:00")
    ]

    mock_db.query.return_value.join.return_value.offset.return_value.limit.return_value = mock_reservations

    room_id = 1
    limit = 2
    offset = 0
    response = await get_reservations(room_id, limit, offset, mock_db)

    assert isinstance(response, ReservationGetAllResponse)
    assert len(response.reservations) == 2
    assert response.reservations[0].user_name == "name 1"
    assert response.reservations[1].user_name == "name 2"

    mock_db.query.return_value.join.return_value.offset.return_value.limit.assert_called_once()


@pytest.mark.parametrize(
    "params, mock_reservations, expected_result",
    [
        (
            RoomCheckAvailabilityRequest(
                id=1,
                start_time=datetime(2025, 2, 1, 10, 0),
                end_time=datetime(2025, 2, 1, 12, 0)
            ),
            [
                Room(id=1, name="Room 1", capacity=10, location="Andar 1"),
            ],
            False
        ),
        (
            RoomCheckAvailabilityRequest(
                id=1,
                start_time=datetime(2025, 2, 1, 13, 0),
                end_time=datetime(2025, 2, 1, 15, 0)
            ),
            [],
            True
        ),
    ]
)
@pytest.mark.asyncio
async def test_check_availability(params, mock_reservations, expected_result):
    mock_db = MagicMock()

    mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_reservations[0] if mock_reservations else None

    response = await check_availability(params, mock_db)

    assert response == expected_result
    if expected_result is False:
        mock_db.query.return_value.join.return_value.filter.return_value.first.assert_called_once()
