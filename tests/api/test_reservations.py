from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    return db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_make_room_reservation(client, mock_db, monkeypatch):
    async def mock_is_reservation_valid(reservation_data, db):
        return True

    async def mock_make_reservation(reservation_data, db):
        return {
            "id": 1,
            "room_id": reservation_data.room_id,
            "user_name": reservation_data.user_name,
            "start_time": reservation_data.start_time,
            "end_time": reservation_data.end_time,
        }

    monkeypatch.setattr(
        "app.api.reservations.is_reservation_valid", mock_is_reservation_valid
    )
    monkeypatch.setattr("app.api.reservations.make_reservation", mock_make_reservation)

    reservation_data = {
        "room_id": 1,
        "user_name": "User 1",
        "start_time": "2025-02-01T10:00:00",
        "end_time": "2025-02-01T12:00:00",
    }

    response = client.post("/reservations/", json=reservation_data)

    assert response.status_code == 200
    data = response.json()

    assert data["room_id"] == 1
    assert data["user_name"] == "User 1"
    assert data["start_time"] == "2025-02-01T10:00:00"
    assert data["end_time"] == "2025-02-01T12:00:00"


@pytest.mark.asyncio
async def test_cancel_room_reservation(client, mock_db, monkeypatch):
    async def mock_cancel_reservation(reservation_id, db):
        return {"message": "Reservation canceled successfully"}

    monkeypatch.setattr(
        "app.api.reservations.cancel_reservation", mock_cancel_reservation
    )

    reservation_id = 1
    response = client.delete(f"/reservations/{reservation_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reservation canceled successfully"


@pytest.mark.asyncio
async def test_make_room_reservation_invalid(client, mock_db, monkeypatch):
    def mock_is_reservation_valid(reservation_data, db):
        return False

    async def mock_make_reservation(reservation_data, db):
        return {
            "id": 1,
            "room_id": reservation_data.room_id,
            "user_name": reservation_data.user_name,
            "start_time": reservation_data.start_time,
            "end_time": reservation_data.end_time,
        }

    monkeypatch.setattr(
        "app.api.reservations.is_reservation_valid", mock_is_reservation_valid
    )
    monkeypatch.setattr("app.api.reservations.make_reservation", mock_make_reservation)

    reservation_data = {
        "room_id": 1,
        "user_name": "User 1",
        "start_time": "2025-02-01T10:00:00",
        "end_time": "2025-02-01T12:00:00",
    }

    response = client.post("/reservations/", json=reservation_data)

    # Verificando se a reserva foi invalidada corretamente
    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "Not a valid reservation"
