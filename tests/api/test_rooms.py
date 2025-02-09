from unittest.mock import MagicMock

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
async def test_create_room(client, mock_db, monkeypatch):
    async def mock_create_room(room_data, db):
        return {
            "id": 1,
            "name": room_data.name,
            "capacity": room_data.capacity,
            "location": room_data.location,
        }

    monkeypatch.setattr("app.api.rooms.create_room", mock_create_room)

    room_data = {"name": "Room 1", "capacity": 10, "location": "Andar 1"}
    response = client.post("/rooms/", json=room_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Room 1"
    assert data["capacity"] == 10


@pytest.mark.asyncio
async def test_get_rooms(client, mock_db, monkeypatch):
    async def mock_get_rooms(limit, offset, db):
        return {
            "rooms": [
                {"id": 1, "name": "Room 1", "capacity": 10, "location": "Andar 1"}
            ]
        }

    monkeypatch.setattr("app.api.rooms.get_rooms", mock_get_rooms)

    response = client.get("/rooms/?limit=1&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["rooms"], list)
    assert len(data["rooms"]) == 1
    assert data["rooms"][0]["name"] == "Room 1"


@pytest.mark.asyncio
async def test_get_room_reservations(client, mock_db, monkeypatch):
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

    response = client.get(f"/rooms/1/reservations?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["reservations"], list)
    assert len(data["reservations"]) == 1
    assert data["reservations"][0]["user_name"] == "User 1"


@pytest.mark.asyncio
async def test_check_room_availability(client, mock_db, monkeypatch):
    async def mock_check_availability(params, db):
        return True

    monkeypatch.setattr("app.api.rooms.check_availability", mock_check_availability)

    response = client.get(
        "/rooms/1/availability?start_time=2025-02-01T10:00:00&end_time=2025-02-01T12:00:00"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Room is available"
