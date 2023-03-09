from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from .database.database import Base
from .main import app, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///../sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db



client = TestClient(app)


def test_users_me():
    response = client.get("/users/me/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    

def test_access_token():
    user_data = {"username":"test",
                 "password":"test"}
    response = client.post("/token", data=user_data,
                           headers={'content-type':'application/x-www-form-urlencoded',
                                    'accept':'application/json'})
    global TOKEN
    TOKEN = response.json()['access_token']
    assert response.status_code == 200
    assert 'access_token' in response.json()
