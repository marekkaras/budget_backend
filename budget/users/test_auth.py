from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from budget.database.crud import create_user, delete_all_users, get_user_by_username
from budget.database.database import get_db
from budget.main import app
from budget.models.user import UserCreate
from budget.tests.utils.utils import (assert_response_success, assert_response_error, 
                                      create_random_email, get_superuser_token_headers)


def test_verify_password():
    hashed_password = "$2b$12$vwK/hJWmk9hRuoiSyJ5wuOe2/qPeZ5JhgfE43mqzGp5n5jKEXJnX."
    assert verify_password("password123", hashed_password)
    assert not verify_password("incorrectpassword", hashed_password)


def test_get_password_hash():
    password = "password123"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)


def test_get_user():
    with get_db() as db:
        user = create_user(db=db, user=UserCreate(username="testuser", email=create_random_email(), password="password"))
        assert user.id is not None

        db_user = get_user(db=db, username=user.username)
        assert db_user.username == user.username


def test_authenticate_user():
    with get_db() as db:
        user = create_user(db=db, user=UserCreate(username="testuser", email=create_random_email(), password="password"))
        assert user.id is not None

        authenticated_user = authenticate_user(db=db, username=user.username, password="password")
        assert authenticated_user.username == user.username

        authenticated_user = authenticate_user(db=db, username=user.username, password="incorrectpassword")
        assert authenticated_user is False


def test_create_access_token():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    access_token = create_access_token(data, expires_delta)
    assert isinstance(access_token, bytes)


def test_get_current_user():
    with get_db() as db:
        user = create_user(db=db, user=UserCreate(username="testuser", email=create_random_email(), password="password"))
        assert user.id is not None

        access_token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {access_token.decode()}"}

        # test that current user can be retrieved from token
        response = app.dependency_overrides[get_db](db).get("/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == user.username

        # test that incorrect token leads to unauthorized error
        headers = {"Authorization": "Bearer invalidtoken"}
        response = app.dependency_overrides[get_db](db).get("/users/me", headers=headers)
        assert response.status_code == 401


def test_get_current_active_user():
    with get_db() as db:
        user = create_user(db=db, user=UserCreate(username="testuser", email=create_random_email(), password="password"))
        assert user.id is not None

        access_token = create_access_token(data={"sub": user.username})
        headers = {"Authorization": f"Bearer {access_token.decode()}"}

        # test that current active user can be retrieved from token
        response = app.dependency_overrides[get_db](db).get("/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == user.username

        # test that inactive user leads to bad request error
        db.execute("UPDATE users SET disabled=true WHERE username=:username", {"username":
