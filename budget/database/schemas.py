from pydantic import BaseModel
import typing


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str
    

class UserRead(UserBase):
    hashed_password: str
    
    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    disabled: bool

    class Config:
        orm_mode = True


class BudgetBase(BaseModel):
    username: str
    amount: float
    base_ccy: str
    month: int
    year: int
    
    class Config:
        orm_mode = True


class Budget(BudgetBase):
    id: int
    uuid: str
    
    class Config:
        orm_mode = True


class Username(BaseModel):
    username: str
    
    class Config:
        orm_mode = True


class AllBudgets(BaseModel):
    budgets: list
