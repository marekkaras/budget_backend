from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from budget.database.models import Base
from budget.database.database import get_db
from budget.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password"
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "test_user",
        "email": "test_user@example.com",
        "id": 1
    }

def test_create_existing_user():
    response = client.post(
        "/create_user/",
        json={
            "username": "test_user",
            "email": "test_user@example.com",
            "password": "password"
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_add_budget_for_user():
    response = client.post(
        "/add_budget_for_user/",
        headers={"Authorization": "Bearer test_token"},
        json={
            "name": "test_budget",
            "description": "test_description",
            "amount": 1000
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "test_budget",
        "description": "test_description",
        "amount": 1000,
        "uuid": 1,
        "user_id": 1,
        "created_at": "2023-03-10T12:00:00",
        "updated_at": "2023-03-10T12:00:00"
    }

def test_add_budget_for_nonexistent_user():
    response = client.post(
        "/add_budget_for_user/",
        headers={"Authorization": "Bearer test_token"},
        json={
            "name": "test_budget",
            "description": "test_description",
            "amount": 1000
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username doesnt exist in database"}
