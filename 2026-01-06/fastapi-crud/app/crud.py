from bson import ObjectId
from app.db import users_collection
from app.models import user_helper_func

def create_users(user_data: dict):
    user = users_collection.insert_one(user_data)
    new_user = users_collection.find_one({"_id": user.inserted_id})
    return user_helper_func(new_user)

def get_users():
    users = []
    for user in users_collection.find():
        users.append(user_helper_func(user))
    return users

def get_user(id: str):
    user = users_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper_func(user)
    return None

def update_users(id: str, data: dict):
    users_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    user = users_collection.find_one({"_id": ObjectId(id)})
    return user_helper_func(user)

def delete_users(id: str):
    result = users_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count

def insert_multiple_users(users: list):
    result = users_collection.insert_many(users)
    inserted_users = users_collection.find(
        {"_id": {"$in": result.inserted_ids}}
    )
    return [user_helper_func(user) for user in inserted_users]
