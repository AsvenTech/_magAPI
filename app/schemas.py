from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime

class Item(BaseModel):
    id: Optional[UUID]
    room_id: UUID
    category_id:UUID
    weight: int
    description: Optional[str]
    found_by_id: UUID

class ItemCreate(BaseModel):
    category_id:UUID
    room_id: UUID
    weight: Optional[int]
    found_date:datetime
    description: Optional[str]
    image_url: str
    booking: Optional[str]
    client_email: Optional[str]
    client_name: Optional[str]
    client_phone_number: Optional[str]


class ListedItems(BaseModel):
    item_id: UUID
    room_number: int
    vip: bool
    image_url: str
    item_weight: int 
    found_date: datetime
    category: str
    status: str

class ItemDetail(ListedItems):
    item_description: str
    found_by: str
    booking: Optional[str]
    client_id: Optional[UUID]
    client_email: Optional[str]
    client_name: Optional[str]
    client_phone_number: Optional[str]
    tracking_number: Optional[str]

class ItemUpdate(BaseModel):
    image_url: str
    description: Optional[str]
    weight: Optional[int]
    room_id: UUID
    category_id:UUID
    found_date:datetime
    found_by_id: UUID
    client_id: Optional[UUID]
    booking: Optional[str]
    client_email: Optional[str]
    client_name: Optional[str]
    client_phone_number: Optional[str]

class ItemResponse(BaseModel):
    id: UUID
    room_id: UUID
    category_id: UUID
    description: Optional[str]
    created_at: datetime
    found_by_id: UUID
    email: Optional[str]

class UserForm(BaseModel):
    id: Optional[UUID]
    username: str
    email: EmailStr
    password: str
    name: str
    role_id: UUID
    hotel_id: UUID
    created_at: Optional[datetime]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    disabled: Optional[bool] = False
    role_id: Optional[UUID]
    hotel_id: UUID
    token: bool = False

class UserDB(User):
    id: UUID
    password: str
    permissions: Optional[List[str]]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

############# Roles #############

class Role(BaseModel):
    id: UUID
    name: str

class RoleCreate(BaseModel):
    name: str
    permissions: List[UUID]

############# CATEGORIES #############

class ListedCategories(BaseModel):
    id: UUID
    name: str
    default_weight: int
    icon_url: Optional[str]
    description: Optional[str]

class CategoryCreate(BaseModel):
    name: str
    default_weight: int
    icon_url: str
    description: str

class CategoryDetail(CategoryCreate):
    id: UUID
    position: int