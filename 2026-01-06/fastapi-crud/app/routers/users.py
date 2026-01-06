from fastapi import APIRouter, HTTPException
from app.schema import UserCreate, UserResponse, UserBulkCreate
from app.crud import (
    create_users,
    get_users,
    get_user,
    update_users,
    delete_users,
    insert_multiple_users
)

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE
@router.post("/", response_model=UserResponse)
def add_user(user: UserCreate):
    return create_users(user.dict())

# READ ALL
@router.get("/", response_model=list[UserResponse])
def list_users():
    return get_users()

# READ ONE
@router.get("/{user_id}", response_model=UserResponse)
def get_single_user(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# UPDATE
@router.put("/{user_id}", response_model=UserResponse)
def update_single_user(user_id: str, user: UserCreate):
    return update_users(user_id, user.dict())

# DELETE
@router.delete("/{user_id}")
def remove_user(user_id: str):
    deleted = delete_users(user_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# BULK INSERT
@router.post("/bulk", response_model=list[UserResponse])
def add_multiple_users(data: UserBulkCreate):
    users = [user.dict() for user in data.users]
    return insert_multiple_users(users)
