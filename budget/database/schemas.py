from pydantic import BaseModel


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
        

class DeleteBudget(BaseModel):
    uuid: str
    
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


class AllocateCategory(BaseModel):
    username: str
    uuid_budget: str
    category_name: str
    amount: float
    
    class Config:
        orm_mode = True
        

class Categories(AllocateCategory):
    id: int
    uuid: str
    
    class Config:
        orm_mode = True
        

class NewCategory(AllocateCategory):
    uuid: str
    
    class Config:
        orm_mode = True
        

class UpdateCategory(BaseModel):
    uuid: str
    category_name: str
    amount: float
    
    class Config:
        orm_mode = True


class BudgetUuid(BaseModel):
    uuid: str
    
    class Config:
        orm_mode = True
        
        
class CategoryUuid(BaseModel):
    uuid: str
    
    class Config:
        orm_mode = True
        

class NewExpense(BaseModel):
    date: str
    uuid_budget: str
    uuid_category: str
    name: str
    amount: float
    base_ccy: str
    exchange_rate: float
    
    class Config:
        orm_mode = True
    
    
class UpdateExpense(BaseModel):
    uuid: str
    date: str
    name: str
    amount: float
    base_ccy: str
    exchange_rate: float
    
    class Config:
        orm_mode = True
        
    
class Expense(NewExpense):
    id: int
    uuid: str
    budget_ccy: str
    budget_amount: float
    
    class Config:
        orm_mode = True
        
class ExpenseUuid(BaseModel):
    uuid: str
    
    class Config:
        orm_mode = True

