import uuid
from sqlalchemy.orm import Session
from budget.database import models, schemas
from passlib.context import CryptContext
from budget.database.database import SessionLocal
from sqlalchemy.exc import NoResultFound


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


def add_budget_for_user(db: Session, data: schemas.BudgetBase, 
                        limit: int = 1000):
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



def get_user_budgets(db: Session, data: schemas.Username, 
                     limit: int = 1000):
    return (db.query(models.Budget)
            .filter(models.Budget.username == data.username)
            .limit(limit).all())


def get_most_recent_user_budgets(db: Session, data: schemas.Username, 
                                 limit: int = 1000):
    res = (db.query(models.Budget)
    .filter(models.Budget.username == data.username).limit(limit).all())
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


def allocate_category_for_budget_uuid(db: Session, 
                                      data: schemas.AllocateCategory, 
                                      limit: int = 1000):
    #  Check if budget exsists
    budget = (db.query(models.Budget)
            .filter(models.Budget.username == data.username)
            .filter(models.Budget.uuid == data.uuid_budget)
            .order_by(models.Budget.id.desc()).first())
    if not budget:
        return  ["No existing budget with given ID"]
    remaning_budget = budget.amount
    #  Get all categories already tied to this budget
    existing_categories = (db.query(models.Categories)
                            .filter(models.Categories.uuid_budget 
                                    == data.uuid_budget)
                            .limit(limit).all())
    #  Decrease remaining budget by already inserted categories
    if len(existing_categories) > 0:
        for existing_category in existing_categories:
            remaning_budget -= existing_category.amount
    #  Sanity check if cateory can be inserted
    if data.amount > remaning_budget:
        msg = f'{data.amount} is higher than remaning budget allowance of '
        msg += f'{remaning_budget}'
        return [msg]
    #  Insert new category
    new_category = models.Categories(uuid_budget=data.uuid_budget,
                                      uuid=str(uuid.uuid4()),
                                      amount=data.amount,
                                      base_ccy=budget.base_ccy,
                                      category_name=data.category_name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return [new_category]


def get_all_categories_for_budget_uuid(db: Session, data: schemas.BudgetUuid, 
                                       limit: int = 1000):
    return (db.query(models.Categories)
            .filter(models.Categories.uuid_budget == data.uuid)
            .limit(limit).all())
    
    
def delete_category_uuid(db: Session, data: schemas.CategoryUuid):
    try:
        query = (db.query(models.Categories)
                .filter(models.Categories.uuid == data.uuid).one())
    except NoResultFound:
        return ["Nothing to remove"]
    db.delete(query)
    db.commit()
    return ["Done"]


def add_expense_to_budget_category(db: Session, data: schemas.NewExpense):
    budget = (db.query(models.Budget)
            .filter(models.Budget.uuid == data.uuid_budget)
            .order_by(models.Budget.id.desc()).first())
    if not budget:
        return  ["No existing budget with given ID"]
    category = (db.query(models.Categories)
            .filter(models.Categories.uuid == data.uuid_category)
            .order_by(models.Categories.id.desc()).first())
    if not category:
        return  ["No existing category with given ID"]
    if budget.base_ccy == data.base_ccy:
        exchange_rate = 1.0
    else:
        exchange_rate = data.exchange_rate
    budget_amount = exchange_rate * data.amount
    new_expense = models.Expense(uuid_budget=data.uuid_budget,
                                 uuid_category=data.uuid_category,
                                 date=data.date,
                                 name=data.name, 
                                 amount=data.amount,
                                 base_ccy=data.base_ccy,
                                 exchange_rate=data.exchange_rate,
                                 uuid=str(uuid.uuid4()),
                                 budget_ccy=budget.base_ccy,
                                 budget_amount=budget_amount)
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


def delete_expense_by_uuid(db: Session, data: schemas.ExpenseUuid):
    try:
        query = (db.query(models.Expense)
                .filter(models.Expense.uuid == data.uuid).one())
    except NoResultFound:
        return ["Nothing to remove"]
    db.delete(query)
    db.commit()
    return ["Done"]


def get_everything_tied_to_budget(db: Session, data: schemas.BudgetUuid, 
                                       limit: int = 1000):
    budget = (db.query(models.Budget)
            .filter(models.Budget.uuid == data.uuid)
            .order_by(models.Budget.id.desc()).first())
    if not budget:
        return  ["No existing budget with given ID"]
    budget = vars(budget)
    budget.pop('_sa_instance_state')
    budget['categories'] = list()
    categories = (db.query(models.Categories)
                .filter(models.Categories.uuid_budget == data.uuid)
                .limit(limit).all())
    if len(categories) == 0:
        return budget
    for category in categories:
        category = vars(category)
        category.pop('_sa_instance_state')
        category['expenses'] = list()
        expenses = (db.query(models.Expense)
                    .filter(models.Expense.uuid_category == category['uuid'])
                    .limit(limit).all())
        if len(expenses) == 0:
            continue
        for expense in expenses:
            expense = vars(expense)
            expense.pop('_sa_instance_state')
            category['expenses'].append(expense)
        budget['categories'].append(category)
    return budget
