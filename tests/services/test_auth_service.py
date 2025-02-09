from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth_service import login_user, register_user


def test_given_valid_data_when_register_user_then_create_and_return_token():
    user_data = UserCreate(username="test_user", password="securepassword")
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    mock_token = "mocked_token"

    with patch(
        "app.services.auth_service.create_access_token", return_value=mock_token
    ):
        response = register_user(user_data, mock_db)

    assert response == mock_token
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_given_existing_user_when_register_user_then_return_error():
    user_data = UserCreate(username="test_user", password="securepassword")
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = User(
        username="test_user", hashed_password="hashedpassword"
    )

    with pytest.raises(HTTPException) as exc_info:
        register_user(user_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "User already exists" in exc_info.value.detail


def test_given_valid_data_when_login_user_then_return_token():
    user_data = UserCreate(username="test_user", password="securepassword")
    mock_db = MagicMock()
    hashed_password = hash_password(user_data.password)
    mock_user = User(username="test_user", hashed_password=hashed_password)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    global verify_password
    verify_password = MagicMock(return_value=True)

    mock_token = "mocked_token"
    with patch(
        "app.services.auth_service.create_access_token", return_value=mock_token
    ):
        response = login_user(user_data, mock_db)

    assert response == mock_token


def test_given_invalid_credentials_when_login_user_then_return_error():
    user_data = UserCreate(username="test_user", password="wrongpassword")
    mock_db = MagicMock()
    hashed_password = hash_password("securepassword")
    mock_user = User(username="test_user", hashed_password=hashed_password)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    global verify_password
    verify_password = MagicMock(return_value=False)

    with pytest.raises(HTTPException) as exc_info:
        login_user(user_data, mock_db)

    assert exc_info.value.status_code == 400
    assert "Invalid credentials" in exc_info.value.detail
