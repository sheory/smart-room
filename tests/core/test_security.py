from datetime import timedelta

from app.core.security import (create_access_token, decode_access_token,
                               hash_password, verify_password)


def test_hash_password():
    password = "testpassword"
    hashed_password = hash_password(password)

    assert hashed_password != password
    assert isinstance(hashed_password, str)
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_verify_password():
    password = "testpassword"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

    decoded_data = decode_access_token(token)
    assert decoded_data["sub"] == "testuser"


def test_decode_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)

    decoded_data = decode_access_token(token)
    assert decoded_data is not None
    assert decoded_data["sub"] == "testuser"

    invalid_token = "invalidtoken"
    decoded_data_invalid = decode_access_token(invalid_token)
    assert decoded_data_invalid is None


def test_create_access_token_expiration():
    data = {"sub": "testuser"}

    token = create_access_token(data, expires_delta=timedelta(seconds=1))

    decoded_data = decode_access_token(token)
    assert decoded_data is not None
