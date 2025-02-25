from datetime import timedelta
from unittest.mock import MagicMock

import pytest
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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_given_room_data_when_create_room_then_return_room(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_create_room(room_data, db):
        return {
            "id": 1,
            "name": room_data.name,
            "capacity": room_data.capacity,
            "location": room_data.location,
        }

    monkeypatch.setattr("app.api.rooms.create_room", mock_create_room)
    headers = {"Authorization": f"Bearer {auth_token}"}

    room_data = {"name": "Room 1", "capacity": 10, "location": "Andar 1"}
    response = client.post("/rooms/", json=room_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Room 1"
    assert data["capacity"] == 10


@pytest.mark.asyncio
async def test_given_room_data_when_create_room_then_raise_exception(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_create_room(room_data, db):
        raise Exception("Database Error")

    monkeypatch.setattr("app.api.rooms.create_room", mock_create_room)

    room_data = {"name": "Room 1", "capacity": 10, "location": "Andar 1"}
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/rooms/", json=room_data, headers=headers)

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_given_db_error_when_get_rooms_then_return_internal_server_error(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_get_rooms(limit, offset, db):
        raise Exception("Database Error")

    monkeypatch.setattr("app.api.rooms.get_rooms", mock_get_rooms)
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/rooms/?limit=1&offset=0", headers=headers)

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_given_db_error_when_get_room_reservations_then_return_internal_error(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_get_reservations(limit, offset, room_id, db):
        raise Exception("Database Error")

    monkeypatch.setattr("app.api.rooms.get_reservations", mock_get_reservations)
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/rooms/1/reservations?limit=1&offset=0", headers=headers)

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_given_db_error_when_check_room_availability_then_return_internal_error(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_check_availability(params, db):
        raise Exception("Database Error")

    monkeypatch.setattr("app.api.rooms.check_availability", mock_check_availability)
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(
        "/rooms/1/availability?start_time=2025-02-01T10:00:00&"
        "end_time=2025-02-01T12:00:00",
        headers=headers,
    )

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_given_valid_request_when_get_rooms_then_return_rooms_list(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_get_rooms(limit, offset, db):
        return {
            "rooms": [
                {"id": 1, "name": "Room 1", "capacity": 10, "location": "Andar 1"}
            ]
        }

    monkeypatch.setattr("app.api.rooms.get_rooms", mock_get_rooms)
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/rooms/?limit=1&offset=0", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["rooms"], list)
    assert len(data["rooms"]) == 1
    assert data["rooms"][0]["name"] == "Room 1"


@pytest.mark.asyncio
async def test_given_valid_request_when_get_room_reservations_then_return_reservations(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_get_reservations(limit, offset, room_id, db):
        print(f"Mock called with room_id={room_id}, limit={limit}, offset={offset}")
        return {
            "reservations": [
                {
                    "id": 1,
                    "room_id": room_id,
                    "user_name": "User 1",
                    "start_time": "2025-02-01T00:00:00",
                    "end_time": "2025-02-01T01:00:00",
                }
            ]
        }

    monkeypatch.setattr("app.api.rooms.get_reservations", mock_get_reservations)

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/rooms/1/reservations?limit=1&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["reservations"], list)
    assert len(data["reservations"]) == 1
    assert data["reservations"][0]["user_name"] == "User 1"


@pytest.mark.asyncio
async def test_given_valid_request_when_check_room_availabilit_then_return_availabilit(
    client, override_get_db, monkeypatch, auth_token, mock_get_current_user
):
    async def mock_check_availability(params, db):
        return True

    monkeypatch.setattr("app.api.rooms.check_availability", mock_check_availability)

    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get(
        "/rooms/1/availability?start_time=2025-02-01"
        "T10:00:00&end_time=2025-02-01T12:00:00",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Room is available"
