from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from budget.api_models.api_models import Token, User
from budget.users.auth import (authenticate_user, create_access_token,
                               get_current_active_user,
                               ACCESS_TOKEN_EXPIRE_MINUTES)
from budget.database import crud, models, schemas
from budget.database.crud import get_db
from budget.database.database import engine
from sqlalchemy.orm import Session

origins = [
    "*"
]

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/create_user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/get_all_users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/get_user/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.post("/add_budget_for_user/", response_model=schemas.Budget)
def add_budget_for_user(data: schemas.BudgetBase, 
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    db_user = crud.get_user_by_username(db, username=data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username doesnt exist in database")
    return crud.add_budget_for_user(db=db, data=data)


@app.post("/delete_budget_for_user/")
def delete_budget_for_user(data: schemas.DeleteBudget, 
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_active_user)):
    return crud.delete_budget_for_user_by_uuid(db=db, data=data)


@app.post("/get_budgets_for_user/")
def get_budgets_for_user(data: schemas.Username, 
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)):
    db_user = crud.get_user_by_username(db, username=data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username doesnt exist in database")
    return crud.get_user_budgets(db=db, data=data)


@app.post("/get_most_recent_budgets_for_user/")
def get_most_recent_budgets_for_user(data: schemas.Username, 
                                     db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_active_user)):
    db_user = crud.get_user_by_username(db, username=data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username doesnt exist in database")
    return crud.get_most_recent_user_budgets(db=db, data=data)


@app.post("/allocate_category_for_budget/")
def allocate_category_for_budget(data: schemas.AllocateCategory, 
                                 db: Session = Depends(get_db),
                                 current_user: User = Depends(get_current_active_user)):
    db_user = crud.get_user_by_username(db, username=data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username doesnt exist in database")
    return crud.allocate_category_for_budget_uuid(db=db, data=data)


@app.post("/get_categories_for_budget/")
def get_categories_for_budget(data: schemas.BudgetUuid, 
                              db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_active_user)):
    return crud.get_all_categories_for_budget_uuid(db=db, data=data)


@app.post("/remove_category_by_uuid/")
def remove_category_by_uuid(data: schemas.CategoryUuid, 
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_active_user)):
    return crud.delete_category_uuid(db=db, data=data)


@app.post("/update_category_by_uuid/")
def update_category_by_uuid(data: schemas.UpdateCategory, 
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_active_user)):
    return crud.update_category_by_id(db=db, data=data)


@app.post("/add_new_expense/")
def add_new_expense(data: schemas.NewExpense, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    return crud.add_expense_to_budget_category(db=db, data=data)


@app.post("/delete_expense/")
def delete_expense(data: schemas.ExpenseUuid, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    return crud.delete_expense_by_uuid(db=db, data=data)


@app.post("/get_budget_summary/")
def get_budget_summary(data: schemas.BudgetUuid, 
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_user)):
    return crud.get_everything_tied_to_budget(db=db, data=data)


@app.post("/get_user_history/")
def get_user_history(db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)):
    return crud.get_full_user_history(db=db, user=current_user)


@app.post("/get_categories_summary/")
def get_categories_summary(db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_active_user)):
    return crud.get_full_categories_summary(db=db, user=current_user)
