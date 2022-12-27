from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str
    

class UserRead(UserBase):
    hashed_password: str


class User(UserBase):
    id: int
    disabled: bool

    class Config:
        orm_mode = True
