import uuid
from sqlalchemy.orm import Session
from budget.database import models, schemas
from passlib.context import CryptContext
from budget.database.database import SessionLocal
from sqlalchemy.exc import NoResultFound
from budget.api_models.api_models import User


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
            .limit(limit).first())
    if res:
        uuid_to_be_used = res.uuid
        res.amount = data.amount
        res.base_ccy = data.base_ccy
        db.commit()
        db.refresh(res)
    else:
        uuid_to_be_used = str(uuid.uuid4())
        res = models.Budget(username=data.username,
                                   uuid=uuid_to_be_used,
                                   amount=data.amount, 
                                   base_ccy=data.base_ccy,
                                   month=data.month,
                                   year=data.year)
        db.add(res)
        db.commit()
        db.refresh(res)
    
    #  Create basic categories for that budget
    for cn in ['Bills', 'Food', 'Entertainment', 'Travel']:
        allocate_category_for_budget_uuid(db=db,
                                          data=schemas.AllocateCategory(username=data.username,
                                                                        uuid_budget=res.uuid,
                                                                        category_name=cn,
                                                                        amount=0.0))
    return res


def delete_budget_for_user_by_uuid(db: Session, data: schemas.DeleteBudget,
                                   limit: int = 1000):
    res = (db.query(models.Budget)
            .filter(models.Budget.uuid == data.uuid)
            .limit(limit).first())
    if not res:
        return 'Nothing to delete'
    res = (db.delete(res))
    db.commit()
    res = (db.query(models.Categories)
            .filter(models.Categories.uuid_budget == data.uuid)
            .limit(limit).all())
    for r in res:
        (db.delete(r))
        db.commit()
    res = (db.query(models.Expense)
            .filter(models.Expense.uuid_budget == data.uuid)
            .limit(limit).all())
    for r in res:
        (db.delete(r))
        db.commit()
    return 'Budget deleted'


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
    #  Insert new category
    res = (db.query(models.Categories)
            .filter(models.Categories.uuid_budget == data.uuid_budget)
            .filter(models.Categories.category_name == data.category_name)
            .limit(limit).first())
    if res:
        res.category_name = data.category_name
        db.commit()
        db.refresh(res)
    else:
        res = models.Categories(uuid_budget=data.uuid_budget,
                                uuid=str(uuid.uuid4()),
                                base_ccy=budget.base_ccy,
                                category_name=data.category_name,
                                amount=data.amount)
        db.add(res)
        db.commit()
        db.refresh(res)
    return [res]


def update_category_by_id(db: Session, 
                          data: schemas.UpdateCategory, 
                          limit: int = 1000):
    category = (db.query(models.Categories)
                .filter(models.Categories.uuid == data.uuid).first())
    if not category:
        return f'Unable to find category with uuid: {data.uuid}'
    category.category_name = data.category_name
    category.amount = data.amount
    db.commit()
    db.refresh(category)
    return f'Category with uuid {data.uuid} updated'


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


def get_category_stats(db: Session, data: schemas.BudgetUuid,
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
        category['spent'] = 0.0
        category['remaining'] = category['amount']
        expenses = (db.query(models.Expense)
                    .filter(models.Expense.uuid_category == category['uuid'])
                    .limit(limit).all())
        if not len(expenses) == 0:
            for expense in expenses:
                expense = vars(expense)
                expense.pop('_sa_instance_state')
                category['spent'] += expense['budget_amount']
                category['remaining'] -= expense['budget_amount']
        budget['categories'].append(category)
    return budget
    
    

def get_full_user_history(db: Session, user: User):
    all_budgets = get_user_budgets(db=db, data=schemas.Username(username=user.username))
    if len(all_budgets) == 0:
        return ['No user budgets found']
    results = []
    for budget in all_budgets:
        results.append(get_everything_tied_to_budget(db=db,
                                                    data=schemas.BudgetUuid(uuid=budget.uuid)))
    return results


def get_full_categories_summary(db: Session, user: User):
    all_budgets = get_user_budgets(db=db, data=schemas.Username(username=user.username))
    if len(all_budgets) == 0:
        return ['No user budgets found']
    results = []
    for budget in all_budgets:
        results.append(get_category_stats(db=db,
                                          data=schemas.BudgetUuid(uuid=budget.uuid)))
    
    return results