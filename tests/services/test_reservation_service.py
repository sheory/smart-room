from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.reservation import Reservation
from app.models.room import Room
from app.schemas.reservations import RerservationCreateRequest
from app.services.reservation_service import (
    cancel_reservation,
    is_reservation_valid,
    make_reservation,
    room_already_reserved_query,
)


@pytest.fixture
def mock_current_time():
    with patch("app.services.reservation_service.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 1, 1, 9, 0)
        yield mock_datetime


@pytest.mark.asyncio
async def test_make_reservation_when_room_does_not_exist_then_return_error():
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
async def test_make_reservation_when_room_is_full_then_return_error():
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
async def test_cancel_reservation_when_success_then_return_message():
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
async def test_cancel_reservation_when_not_found_then_return_message():
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
def test_is_reservation_valid_time_when_start_time_is_after_end_time_then_raise_error(
    mock_current_time, start_time, end_time, should_raise, expected_detail
):
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
def test_is_reservation_valid_room_when_room_does_not_exist_or_is_full_then_raise(
    mock_current_time, room_exists, room_capacity, should_raise, expected_detail
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
def test_is_reservation_valid_already_reserved_when_room_is_alread_reserved_then_raise(
    mock_current_time, already_reserved, should_raise, expected_detail
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


@pytest.mark.parametrize(
    "start_time, should_raise, expected_detail",
    [
        (datetime(2025, 2, 1, 10, 0), False, None),
        (
            datetime(2023, 2, 1, 10, 0),
            True,
            "datetime not valid, start_time should be greater or equal now.",
        ),
    ],
)
def test_is_reservation_valid_start_time_when_start_time_is_before_now_then_raise(
    mock_current_time, start_time, should_raise, expected_detail
):
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=start_time,
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = False

    if should_raise:
        with pytest.raises(Exception) as exc_info:
            is_reservation_valid(reservation_data, mock_db)
        assert exc_info.value.detail == expected_detail
    else:
        result = is_reservation_valid(reservation_data, mock_db)
        assert result is True


@pytest.mark.asyncio
async def test_make_reservation_when_success_then_return_reservation_details():
    reservation_data = RerservationCreateRequest(
        room_id=1,
        user_name="test1",
        start_time=datetime(2025, 2, 1, 10, 0),
        end_time=datetime(2025, 2, 1, 12, 0),
    )

    mock_db = MagicMock()
    mock_room = Room(id=1, capacity=5)
    mock_db.get.return_value = mock_room

    with patch(
        "app.services.reservation_service.ReservationModel"
    ) as mock_reservation_model:
        mock_reservation = MagicMock()
        mock_reservation.id = 1
        mock_reservation.user_name = reservation_data.user_name
        mock_reservation.room_id = reservation_data.room_id
        mock_reservation.start_time = reservation_data.start_time
        mock_reservation.end_time = reservation_data.end_time

        mock_reservation_model.return_value = mock_reservation

        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        response = await make_reservation(reservation_data, mock_db)

        assert response.user_name == "test1"
        assert response.room_id == 1
        assert mock_room.capacity == 4
        mock_db.add.assert_called_once_with(mock_reservation)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_room_already_reserved_query_when_room_is_reserved_then_return_it():
    start_time = datetime(2025, 2, 1, 10, 0)
    end_time = datetime(2025, 2, 1, 12, 0)

    mock_db = MagicMock()
    mock_reserved = Reservation(room_id=1, start_time=start_time, end_time=end_time)
    mock_db.query().filter().first.return_value = mock_reserved

    result = room_already_reserved_query(start_time, end_time, 1, mock_db)

    assert result == mock_reserved
