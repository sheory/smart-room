import pytest
from unittest.mock import MagicMock
from app.models.room import Room
from datetime import datetime

from app.schemas.reservations import RerservationCreateRequest
from app.services.reservation_service import cancel_reservation, make_reservation

"""@pytest.mark.parametrize(
    "reservation_data, expected_result",
    [
        (
            RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0)),
            True
        ),
        (
            RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 12, 0), end_time=datetime(2025, 2, 1, 10, 0)),
            False
        ),
        (
            RerservationCreateRequest(room_id=2, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0)),
            False
        ),
        (
            RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0)),
            False
        )
    ]
)
def test_is_reservation_valid(reservation_data, expected_result):
    mock_db = MagicMock()
    if expected_result is False:
        mock_db.get.side_effect = lambda model, id: None
    else:
        mock_db.get.return_value = Room(id=1, capacity=5)
        mock_db.query.return_value.filter.return_value.first.return_value = None

    response = is_reservation_valid(reservation_data, mock_db)
    assert response == expected_result
"""

@pytest.mark.asyncio
async def test_make_reservation_success():
    reservation_data = RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0))
    mock_db = MagicMock()
    mock_db.get.return_value = Room(id=1, capacity=5)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    response = await make_reservation(reservation_data, mock_db)

    assert isinstance(response, RerservationCreateRequest)
    assert response.room_id == reservation_data.room_id

"""
@pytest.mark.asyncio
async def test_make_reservation_room_not_exist():
    reservation_data = RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0))

    mock_db = MagicMock()
    mock_db.get.return_value = None

    response = await make_reservation(reservation_data, mock_db)

    assert response == {"error": "room does not exist."}


@pytest.mark.asyncio
async def test_make_reservation_room_full():
    reservation_data = RerservationCreateRequest(room_id=1, start_time=datetime(2025, 2, 1, 10, 0), end_time=datetime(2025, 2, 1, 12, 0))

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

    assert response == {"message": "reservation not found"}"""