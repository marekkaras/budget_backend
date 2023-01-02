from sqlalchemy import Boolean, Column, Integer, String, Float
from budget.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=True)


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    amount = Column(Float)
    base_ccy = Column(String)
    month = Column(Integer)
    year = Column(Integer)
