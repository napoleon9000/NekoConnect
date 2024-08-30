from tinydb import TinyDB, Query
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import uuid
from typing import List

# Initialize the database
db = TinyDB('nekoconnect_db.json')
users_table = db.table('users')


@dataclass
class Redemption:
    item: str
    date: str
    credits: int


@dataclass
class User:
    uuid: str
    phone_number: str
    registration_date: str
    credits: int = 0
    name: str = ""
    redemption_history: List[Redemption] = None
    
    def __post_init__(self):
        if self.redemption_history is None:
            self.redemption_history = []



# Create a new user
def create_user(phone_number, name=None):
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_uuid = str(uuid.uuid4())
    user = User(user_uuid, phone_number, registration_date, name=name)
    users_table.insert(user.__dict__)

# Edit user information
def edit_user(phone_number, name=None, credits=None):
    UserQuery = Query()
    updates = {}
    if name:
        updates['name'] = name
    if credits is not None:
        updates['credits'] = credits
    users_table.update(updates, UserQuery.phone_number == phone_number)

# Delete a user
def delete_user(phone_number):
    UserQuery = Query()
    users_table.remove(UserQuery.phone_number == phone_number)

# Find a user
def find_user(phone_number):
    UserQuery = Query()
    return users_table.search(UserQuery.phone_number == phone_number)

# Record redemption
def record_redemption(phone_number, item):
    user_data = find_user(phone_number)
    if user_data:
        user = user_data[0]
        user['redemption_history'].append({"item": item, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        edit_user(phone_number, credits=user['credits'], name=user['name'])

# all users to pandas dataframe
def all_users_to_df():
    return pd.DataFrame(users_table.all())

# display user info on home page
def display_user_info():
    display_keys = ['phone_number', 'name', 'credits', 'registration_date']
    all_users = all_users_to_df()
    return all_users[display_keys]

# record redemption
def record_redemption(phone_number, item, credits):
    user_data = find_user(phone_number)
    if user_data:
        UserQuery = Query()
        user = user_data[0]
        current_history = user['redemption_history']
        current_credits = user['credits']
        current_history.append({"item": item, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "credits": credits})
        new_credits = current_credits - credits
        if new_credits < 0:
            raise ValueError("Not enough credits!")

        updates = {'redemption_history': current_history, 'credits': new_credits}
        users_table.update(updates, UserQuery.phone_number == phone_number)