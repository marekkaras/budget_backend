# -*- coding: utf-8 -*-
import requests
import json
import random

#  Start by generating user
user_data = {
  "username": "test",
  "email": "test@test.com",
  "full_name": "Test User",
  "password": "test"
}
response = requests.post('http://127.0.0.1:8045/create_user/',
                        json=user_data,        
                        headers={'content-type':'application/json',
                                 'accept':'application/json'},)
print(response.text)


#  Get user token
user_data = {'grant_type':'',
             'username':'test',
             'password':'test',
             'scope':'',
             'client_id':'',
             'client_secret':''}
response = requests.post('http://127.0.0.1:8045/token',
                        data=user_data,        
                        headers={'content-type':'application/x-www-form-urlencoded',
                                 'accept':'application/json'},)
r = json.loads(response.text)
token_data = f'{r["token_type"]} {r["access_token"]}'
print(token_data)


#  Create new budget for 01/2023
user_data = {
  "username": "test",
  "amount": 2000,
  "base_ccy": "USD",
  "month": 1,
  "year": 2023
}
response = requests.post('http://127.0.0.1:8045/add_budget_for_user/',
                        json=user_data,        
                        headers={'Authorization':token_data,
                                'content-type':'application/json',
                                 'accept':'application/json'},)
print(response.text)
budget_uuid = json.loads(response.text)['uuid']
print(budget_uuid)


#  Get all categories for budget
user_data = {
  "uuid": budget_uuid
}
response = requests.post('http://127.0.0.1:8045/get_categories_for_budget/',
                        json=user_data,        
                        headers={'Authorization':token_data,
                                'content-type':'application/json',
                                 'accept':'application/json'},)
print(response.text)
categories = json.loads(response.text)


#  Update category amount
for cat in categories:
    user_data = {
          "uuid": cat['uuid'],
          "category_name": cat['category_name'],
          "amount": 500
        }
    response = requests.post('http://127.0.0.1:8045/update_category_by_uuid/',
                                json=user_data,        
                                headers={'Authorization':token_data,
                                        'content-type':'application/json',
                                         'accept':'application/json'},)
    print(response.text)

#  Add some random expenses
for cat in categories:
    print(cat)
    for i in range(0,random.randint(2,5)):
        expense_name = f'Random Expense {i}'
        user_data = {
          "date": "2023-01-01",
          "uuid_budget": budget_uuid,
          "uuid_category": cat['uuid'],
          "name": expense_name,
          "amount": random.randrange(10,100),
          "base_ccy": "USD",
          "exchange_rate": 1.0
        }
        response = requests.post('http://127.0.0.1:8045/add_new_expense/',
                                json=user_data,        
                                headers={'Authorization':token_data,
                                        'content-type':'application/json',
                                         'accept':'application/json'},)
        print(response.text)
