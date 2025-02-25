from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.settings import get_db
from app.schemas.user import UserBase
from main import app


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)
    db.query().filter().first().username = "user_name"
    return db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token():
    user_data = {"sub": "test_user"}
    token = create_access_token(user_data, expires_delta=timedelta(hours=1))
    return token


@pytest.fixture
def mock_get_current_user(mock_db, monkeypatch):
    def _mock_get_current_user(
        token: str = "fake_token", db: Session = mock_db
    ) -> UserBase:
        return UserBase(username="test_user")

    monkeypatch.setattr("app.api.reservations.get_current_user", _mock_get_current_user)


@pytest.fixture
def override_get_db(mock_db):
    def _get_db_override():
        yield mock_db

    app.dependency_overrides[get_db] = _get_db_override


@pytest.mark.asyncio
async def test_make_room_reservation(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    def mock_is_reservation_valid(reservation_data, db):
        return True

    async def mock_make_reservation(reservation_data, db):
        return {
            "id": 1,
            "room_id": reservation_data.room_id,
            "user_name": reservation_data.user_name,
            "start_time": reservation_data.start_time,
            "end_time": reservation_data.end_time,
        }

    headers = {"Authorization": f"Bearer {auth_token}"}

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

    response = client.post("/reservations/", json=reservation_data, headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["room_id"] == 1
    assert data["user_name"] == "User 1"
    assert data["start_time"] == "2025-02-01T10:00:00"
    assert data["end_time"] == "2025-02-01T12:00:00"


@pytest.mark.asyncio
async def test_cancel_room_reservation(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_cancel_reservation(reservation_id, db, username):
        return {"message": "Reservation canceled successfully"}

    headers = {"Authorization": f"Bearer {auth_token}"}
    monkeypatch.setattr(
        "app.api.reservations.cancel_reservation", mock_cancel_reservation
    )

    reservation_id = 1
    response = client.delete(f"/reservations/{reservation_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Reservation canceled successfully"


@pytest.mark.asyncio
async def test_cancel_room_reservation_error(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_cancel_reservation(reservation_id, db, username):
        raise HTTPException(detail="Error cancelling reservation", status_code=500)

    monkeypatch.setattr(
        "app.api.reservations.cancel_reservation", mock_cancel_reservation
    )

    headers = {"Authorization": f"Bearer {auth_token}"}

    reservation_id = 1
    response = client.delete(f"/reservations/{reservation_id}", headers=headers)

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Error cancelling reservation" in data["detail"]


@pytest.mark.asyncio
async def test_make_room_reservation_invalid(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
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

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/reservations/", json=reservation_data, headers=headers)

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Not a valid reservation"
