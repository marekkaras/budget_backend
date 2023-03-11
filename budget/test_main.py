import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from budget.database.models import Base
from budget.database.crud import get_db
from budget.main import app
from budget.database import models

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

    user = models.User(
        username="test_user",
        email="test_user@example.com",
        hashed_password="password",
        full_name="Test User",
        disabled=False
    )

    return {"user": user, "token": "test_token"}


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_user(db):
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password",
            "full_name": "Test User"
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test_user@example.com"
    assert response.json()["full_name"] == "Test User"
    assert response.json()["hashed_password"] is not None
    assert response.json()["hashed_password"] != "password"


def test_create_existing_user(db):
    # Create a user
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password",
            "full_name": "Test User"
        },
    )

    # Make sure the user was created successfully
    assert response.status_code == 200

    # Try to create the same user again
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password",
            "full_name": "Test User"
        },
    )

    # Make sure the endpoint returns a 400 status code and an error message
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}


def test_add_budget_for_user():
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user_2",
            "email": "test_user_2@example.com",
            "password": "password",
            "full_name": "Test User"
        },
    )

    form_data = {
        "username": "test_user_2",
        "password": "password"
    }
    token_response = client.post("/token", data=form_data)
    access_token = token_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "base_ccy": "USD",
        "month": 3,
        "year": 2023,
        "amount": 1000
    }

    response = client.post("/add_budget_for_user/", headers=headers, json=data)

    assert response.status_code == 200

    assert response.json()["base_ccy"] == "USD"
    assert response.json()["amount"] == 1000.0
    assert response.json()["month"] == 3
    assert response.json()["year"] == 2023


def test_add_budget_for_nonexistent_user():
    response = client.post(
        "/add_budget_for_user/",
        headers={"Authorization": "Bearer test_token"},
        json={
            "base_ccy": "USD",
            "month": 3,
            "year": 2023,
            "amount": 1000
        }
    )
    assert response.status_code == 401
