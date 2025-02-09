from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.models.room import Room
from app.schemas.reservations import RerservationCreateRequest
from app.services.reservation_service import (
    cancel_reservation,
    is_reservation_valid,
    make_reservation,
)


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

    assert response == {"error": "Room does not exists."}


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

    assert response == {"error": "Room capacity is already full."}


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

    assert response == {"message": "Reservation cancelled successfully."}


@pytest.mark.asyncio
async def test_cancel_reservation_not_found():
    reservation_id = 999

    mock_db = MagicMock()
    mock_db.get.return_value = None

    response = await cancel_reservation(reservation_id, mock_db)

    assert response == {"message": "Reservation not found"}


@pytest.mark.parametrize(
    "start_time, end_time, should_raise, expected_detail",
    [
        (
            datetime(2025, 2, 1, 12, 0),
            datetime(2025, 2, 1, 10, 0),
            True,
            "datetime not valid",
        ),
        (datetime(2025, 2, 1, 10, 0), datetime(2025, 2, 1, 12, 0), False, None),
    ],
)
def test_is_reservation_valid_time(start_time, end_time, should_raise, expected_detail):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=start_time,
        end_time=end_time,
    )

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = False
    if should_raise:
        with pytest.raises(Exception) as exc_info:
            is_reservation_valid(reservation_data, mock_db)
        assert exc_info.value.status_code == 400
        assert (
            exc_info.value.detail
            == "datetime not valid, start_time should be lower than end_time."
        )
    else:
        result = is_reservation_valid(reservation_data, mock_db)
        assert result is True


@pytest.mark.parametrize(
    "room_exists, room_capacity, should_raise, expected_detail",
    [
        (False, 5, True, "Room does not exists."),
        (True, 0, True, "Room capacity is already full."),
        (True, 5, False, None),
    ],
)
def test_is_reservation_valid_room(
    room_exists, room_capacity, should_raise, expected_detail
):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_room = Room(id=1, capacity=room_capacity) if room_exists else None
    mock_db.get.return_value = mock_room
    mock_db.query().filter().first.return_value = False

    if should_raise:
        with pytest.raises(Exception) as exc_info:
            is_reservation_valid(reservation_data, mock_db)
        assert exc_info.value.detail == expected_detail
    else:
        result = is_reservation_valid(reservation_data, mock_db)
        assert result is True


@pytest.mark.parametrize(
    "already_reserved, should_raise, expected_detail",
    [
        (True, True, "Room already reserved for this date."),
        (False, False, None),
    ],
)
def test_is_reservation_valid_already_reserved(
    already_reserved, should_raise, expected_detail
):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = already_reserved

    if should_raise:
        with pytest.raises(Exception) as exc_info:
            is_reservation_valid(reservation_data, mock_db)
        assert exc_info.value.detail == expected_detail
    else:
        result = is_reservation_valid(reservation_data, mock_db)
        assert result is True
