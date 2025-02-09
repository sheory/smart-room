from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.models.room import Room
from app.schemas.reservations import RerservationCreateRequest
from app.services.reservation_service import (cancel_reservation,
                                              is_reservation_valid,
                                              make_reservation)


@pytest.mark.asyncio
async def test_make_reservation_room_not_exist():
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_db.get.return_value = None

    response = await make_reservation(reservation_data, mock_db)

    assert response == {"error": "room does not exist."}


@pytest.mark.asyncio
async def test_make_reservation_room_full():
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_db.get.return_value = Room(id=1, capacity=0)

    response = await make_reservation(reservation_data, mock_db)

    assert response == {"error": "room capacity is already full."}


@pytest.mark.asyncio
async def test_cancel_reservation_success():
    reservation_id = 1

    mock_db = MagicMock()
    mock_reservation = MagicMock()
    mock_reservation.room_id = 1
    mock_db.get.return_value = mock_reservation
    mock_db.delete = MagicMock()
    mock_db.commit = MagicMock()

    response = await cancel_reservation(reservation_id, mock_db)

    assert response == {"message": "reservation cancelled successfully."}


@pytest.mark.asyncio
async def test_cancel_reservation_not_found():
    reservation_id = 999

    mock_db = MagicMock()
    mock_db.get.return_value = None

    response = await cancel_reservation(reservation_id, mock_db)

    assert response == {"message": "reservation not found"}


@pytest.mark.parametrize(
    "start_time, end_time, expected_result",
    [
        (datetime(2025, 2, 1, 10, 0), datetime(2025, 2, 1, 12, 0), True),
        (datetime(2025, 2, 1, 12, 0), datetime(2025, 2, 1, 10, 0), False),
    ],
)
@pytest.mark.asyncio
async def test_is_reservation_valid_time(start_time, end_time, expected_result):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=start_time,
        end_time=end_time,
    )

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = False
    result = is_reservation_valid(reservation_data, mock_db)

    assert result == expected_result


@pytest.mark.parametrize(
    "room_exists, room_capacity, expected_result",
    [
        (True, 5, True),
        (True, 0, False),
        (False, 5, False),
    ],
)
@pytest.mark.asyncio
async def test_is_reservation_valid_room(room_exists, room_capacity, expected_result):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    result = is_reservation_valid(reservation_data, mock_db)

    mock_room = Room(id=1, capacity=room_capacity) if room_exists else None
    mock_db.get.return_value = mock_room
    mock_db.query().filter().first.return_value = False

    result = is_reservation_valid(reservation_data, mock_db)

    assert result == expected_result


@pytest.mark.parametrize(
    "already_reserved, expected_result",
    [
        (True, False),
        (False, True),
    ],
)
@pytest.mark.asyncio
async def test_is_reservation_valid_already_reserved(already_reserved, expected_result):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = already_reserved

    result = is_reservation_valid(reservation_data, mock_db)

    assert result == expected_result
