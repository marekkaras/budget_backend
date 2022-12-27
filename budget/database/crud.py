from sqlalchemy.orm import Session
from budget.database import models, schemas
from passlib.context import CryptContext
from budget.database.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username,
                          email=user.email, 
                          full_name=user.full_name,
                          hashed_password=get_password_hash(user.password),
                          disabled=False)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
