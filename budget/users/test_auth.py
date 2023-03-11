from budget.users.auth import (
    verify_password, get_password_hash, get_user, authenticate_user, create_access_token)
from datetime import timedelta
from budget.database import schemas
from budget.database.crud import create_user
from budget.database.crud import get_db
from budget.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from budget.database.models import Base
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_verify_password():
    password = "password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password("incorrectpassword", hashed_password)


def test_get_password_hash():
    password = "password123"
    hashed_password = get_password_hash(password)
    assert not password == hashed_password


def test_authenticate_user(db):
    session = TestingSessionLocal()

    user = create_user(db=session, user=schemas.UserCreate(
        username="test_user_3", email="testuser@test.com", password="password", full_name="test user"))
    assert user.id is not None

    authenticated_user = authenticate_user(
        db=session, username=user.username, password="password")
    assert authenticated_user.username == user.username

    authenticated_user = authenticate_user(
        db=session, username=user.username, password="incorrectpassword")
    assert authenticated_user is False


def test_create_access_token():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)
    access_token = create_access_token(data, expires_delta)
    assert "ey" in access_token
