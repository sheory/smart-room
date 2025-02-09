from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.reservation import Reservation
from app.models.room import Room
from app.schemas.reservations import ReservationGetAllResponse
from app.schemas.rooms import (
    RoomCheckAvailabilityRequest,
    RoomCreateRequest,
    RoomGetAllResponse,
)
from app.services.room_service import (
    check_availability,
    create_room,
    get_reservations,
    get_rooms,
)


@pytest.fixture(autouse=True)
def mock_room_model():
    mock = MagicMock()
    mock.return_value.__dict__ = {
        "id": 1,
        "name": "Room 1",
        "capacity": 10,
        "location": "Andar 1",
    }
    with patch("app.services.room_service.RoomModel", mock):
        yield mock


@pytest.mark.asyncio
async def test_create_room_successfully_creates_room():
    mock_db = MagicMock()
    room_data = RoomCreateRequest(name="Room 1", capacity=10, location="Andar 1")

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    response = await create_room(room_data, mock_db)

    assert response.name == "Room 1"
    assert response.capacity == 10
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_create_room_with_invalid_capacity_raises_exception():
    mock_db = MagicMock()
    room_data = RoomCreateRequest(name="Room 1", capacity=0, location="Andar 1")

    with pytest.raises(HTTPException) as exc_info:
        await create_room(room_data, mock_db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Room capacity should be greater than 0"


@pytest.mark.asyncio
async def test_get_rooms_successfully_returns_rooms():
    mock_db = MagicMock()

    mock_rooms = [
        Room(id=1, name="Room 1", capacity=10, location="Andar 1"),
        Room(id=2, name="Room 2", capacity=15, location="Andar 2"),
    ]

    mock_db.query().offset().limit().all.return_value = mock_rooms

    limit = 2
    offset = 0
    response = await get_rooms(limit, offset, mock_db)

    assert isinstance(response, RoomGetAllResponse)

    assert len(response.rooms) == 2
    assert response.rooms[0].name == "Room 1"
    assert response.rooms[1].name == "Room 2"

    mock_db.query().offset().limit().all.assert_called_once()


@pytest.mark.asyncio
async def test_get_rooms_with_exception_handling():
    mock_db = MagicMock()
    mock_db.query().offset().limit().all.side_effect = Exception("Database error")

    limit = 2
    offset = 0
    with pytest.raises(HTTPException) as exc_info:
        await get_rooms(limit, offset, mock_db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error getting rooms"
    mock_db.query().offset().limit().all.assert_called_once()


@pytest.mark.asyncio
async def test_get_reservations_successfully_returns_reservations():
    mock_db = MagicMock()

    mock_reservations = [
        Reservation(
            id=1,
            room_id=1,
            user_name="name 1",
            start_time="2025-02-01T00:00:00",
            end_time="2025-02-01T01:00:00",
        ),
        Reservation(
            id=2,
            room_id=1,
            user_name="name 2",
            start_time="2025-02-02T00:00:00",
            end_time="2025-02-02T01:00:00",
        ),
    ]

    mock_db.query().join().offset().limit.return_value = mock_reservations

    room_id = 1
    limit = 2
    offset = 0
    response = await get_reservations(room_id, limit, offset, mock_db)

    assert isinstance(response, ReservationGetAllResponse)
    assert len(response.reservations) == 2
    assert response.reservations[0].user_name == "name 1"
    assert response.reservations[1].user_name == "name 2"

    mock_db.query().join().offset().limit.assert_called_once()


@pytest.mark.asyncio
async def test_get_reservations_with_exception_handling():
    mock_db = MagicMock()
    mock_db.query().join().offset().limit.side_effect = Exception("Database error")

    room_id = 1
    limit = 2
    offset = 0
    with pytest.raises(HTTPException) as exc_info:
        await get_reservations(room_id, limit, offset, mock_db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Error getting reservations"
    mock_db.query().join().offset().limit.assert_called_once()


@pytest.mark.parametrize(
    "params, mock_reservations, expected_result",
    [
        (
            RoomCheckAvailabilityRequest(
                id=1,
                start_time=datetime(2025, 2, 1, 10, 0),
                end_time=datetime(2025, 2, 1, 12, 0),
            ),
            [
                Room(id=1, name="Room 1", capacity=10, location="Andar 1"),
            ],
            False,
        ),
        (
            RoomCheckAvailabilityRequest(
                id=1,
                start_time=datetime(2025, 2, 1, 13, 0),
                end_time=datetime(2025, 2, 1, 15, 0),
            ),
            [],
            True,
        ),
    ],
)
@pytest.mark.asyncio
async def test_check_availability_successful_availability_check(
    params, mock_reservations, expected_result
):
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_reservations[0] if mock_reservations else None
    )

    response = await check_availability(params, mock_db)

    assert response is expected_result

    if expected_result is False:
        mock_db.query.return_value.filter.return_value.first.assert_called_once()


@pytest.mark.asyncio
async def test_check_availability_when_room_is_already_reserved():
    mock_db = MagicMock()

    mock_db.query().filter().first.return_value = Room(
        id=1, name="Room 1", capacity=10, location="Andar 1"
    )

    params = RoomCheckAvailabilityRequest(
        id=1,
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    result = await check_availability(params, mock_db)

    assert result is False
    mock_db.query().filter().first.assert_called_once()


@pytest.mark.asyncio
async def test_check_availability_when_room_is_not_reserved():
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None

    params = RoomCheckAvailabilityRequest(
        id=1,
        start_time=datetime(2025, 2, 1, 13, 0),
        end_time=datetime(2025, 2, 1, 15, 0),
    )

    result = await check_availability(params, mock_db)

    assert result is True
    mock_db.query().filter().first.assert_called_once()
