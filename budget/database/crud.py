import uuid
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


def add_budget_for_user(db: Session, data: schemas.BudgetBase, limit: int = 1000):
    #  check if there was a budget a given month already, reuse uuid if so
    res = (db.query(models.Budget)
            .filter(models.Budget.month == data.month)
            .filter(models.Budget.year == data.year)
            .filter(models.Budget.username == data.username)
            .limit(limit).all())
    if len(res) > 0:
        uuid_to_be_used = res[0].uuid
    else:
        uuid_to_be_used = str(uuid.uuid4())
    new_budget = models.Budget(username=data.username,
                               uuid=uuid_to_be_used,
                               amount=data.amount, 
                               base_ccy=data.base_ccy,
                               month=data.month,
                               year=data.year)
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget



def get_user_budgets(db: Session, data: schemas.Username, limit: int = 1000):
    return db.query(models.Budget).filter(models.Budget.username == data.username).limit(limit).all()


def get_most_recent_user_budgets(db: Session, data: schemas.Username, limit: int = 1000):
    res = db.query(models.Budget).filter(models.Budget.username == data.username).limit(limit).all()
    recent_budgets = dict()
    for entry in res:
        if entry.uuid not in recent_budgets:
            recent_budgets[entry.uuid] = entry
        else:
            if entry.id > recent_budgets[entry.uuid].id:
                recent_budgets[entry.uuid] = entry
    result = list()
    for v in recent_budgets.values():
        result.append(v)
    return result
