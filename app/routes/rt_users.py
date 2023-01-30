from fastapi import Response, status, HTTPException, APIRouter
from typing import List
from app.schemas import Item, ItemResponse, User, UserForm
from app.utils.u_db import query
from app.utils.u_auth import get_password_hash
from app.utils import u_auth

from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"],)
#hotel_id = "45c94235-c45b-4329-8807-5a72dd164d5f"
##role_id = "b053c50b-7f08-406b-9265-b8fe225e3269"

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=User)
def create_user(user: UserForm):
    hashed = get_password_hash(user.password)
    new_user = query(f"""INSERT INTO users (hotel_id, role_id, username, email, password, name ) VALUES ('{user.hotel_id}', '{user.role_id}', '{user.username}', '{user.email}', '{hashed}','{user.name}'  ) RETURNING *""")
    print("HEYY")
    return new_user

@router.get("/{id}")
def get_user(id: UUID):
    user = query(f""" SELECT * FROM users WHERE id = '{id}'""")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items to show")
    return user
