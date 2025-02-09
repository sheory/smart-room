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


def test_register(client, mock_db, monkeypatch):
    def mock_register_user(user_data, db):
        return "mocked_token"

    monkeypatch.setattr("app.api.auth.register_user", mock_register_user)

    user_data = {"username": "testuser", "password": "testpassword"}

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] == "mocked_token"
    assert data["token_type"] == "bearer"


def test_login(client, mock_db, monkeypatch):
    def mock_login_user(user_data, db):
        return "mocked_token"

    monkeypatch.setattr("app.api.auth.login_user", mock_login_user)

    user_data = {"username": "testuser", "password": "testpassword"}

    response = client.post("/auth/login", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] == "mocked_token"
    assert data["token_type"] == "bearer"
