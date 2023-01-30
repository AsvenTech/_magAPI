
from fastapi import Response, status, HTTPException, APIRouter, Depends
from typing import List
from app.schemas import Item, ItemResponse, ItemCreate,ListedItems,ItemDetail, UserDB, ItemUpdate
from app.utils.u_db import query
from app.utils.u_auth import get_current_user, get_user
from uuid import UUID

router = APIRouter(prefix="/items", tags=["items"],)

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=ItemResponse)
def create_item(item: ItemCreate, user: UserDB = Depends(get_current_user)):
    if 'create' not in user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You dont have permissions to perform this action", headers={"WWW-Authenticate": "Bearer"})
    new_item = query(f"""INSERT INTO items 
                        (hotel_id, category_id, found_by_id, room_id, weight, found_date, description, image_url) 
                        VALUES ('{user.hotel_id}', '{item.category_id}', '{user.id}', '{item.room_id}', '{item.weight}', '{item.found_date}', '{item.description}', '{item.image_url}') RETURNING *""")
    if item.booking or item.client_email:
        new_client = query(f"""INSERT INTO clients 
                        (hotel_id, room_id, email, phone_number, name, booking) 
                        VALUES ('{user.hotel_id}', '{item.room_id}', '{item.client_email}', '{item.client_phone_number}', '{item.client_name}', '{item.booking}') RETURNING *""")
        query(f"""UPDATE items SET client_id = '{new_client['id']}' WHERE id = '{new_item['id']}' RETURNING *""")             
    return new_item

@router.get("/", response_model=List[ListedItems])
def get_items(user: UserDB = Depends(get_current_user), filter: str = ''):
    if filter == '':
        no_filter = '--'
    else:
        no_filter = ''
    items = query(f"""SELECT items.id as item_id,
                        rooms.room_number,
                        rooms.vip,
                        items.image_url,
                        items.weight as item_weight,
                        items.found_date,
                        categories.name as category,
                        item_status.name as status
                    FROM public.items
                        LEFT JOIN public.categories ON categories.id = items.category_id
                        LEFT JOIN public.item_status ON item_status.id = items.status_id
                        LEFT JOIN public.rooms ON rooms.id = items.room_id
                    {no_filter}WHERE item_status.name = '{filter}'    
                        """)
    print(filter)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items to show")
    return items
    
@router.get("/user/", response_model=List[ListedItems])
def get_items_user(user: UserDB = Depends(get_current_user), filter: str = ''):
    if filter == '':
        no_filter = '--'
    else:
        no_filter = ''
    items = query(f"""SELECT items.id as item_id,
                        rooms.room_number,
                        rooms.vip,
                        items.image_url,
                        items.weight as item_weight,
                        items.found_date,
                        categories.name as category,
                        item_status.name as status
                    FROM public.items
                        LEFT JOIN public.categories ON categories.id = items.category_id
                        LEFT JOIN public.item_status ON item_status.id = items.status_id
                        LEFT JOIN public.rooms ON rooms.id = items.room_id
                    {no_filter}WHERE status = '{filter}' AND items.found_by_id = '{user.id}'   
                        """)
    print(filter)
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items to show")
    return items

@router.get("/{id}", response_model=ItemDetail)
def get_item(id: UUID):
    item = query(f""" SELECT items.id as item_id,
                        rooms.room_number,
                        rooms.vip,
                        items.image_url,
                        items.description as item_description,
                        items.weight as item_weight,
                        items.found_date,
                        categories.name as category,
                        item_status.name as status,
                        users.name as found_by,
                        items.client_id as client_id,
                        clients.booking,
                        clients.email as client_email,
                        clients.name as client_name,
                        clients.phone_number as client_phone_number,
                        shipment.tracking_number as tracking_number
                    FROM public.items
                        LEFT JOIN public.categories ON categories.id = items.category_id
                        LEFT JOIN public.item_status ON item_status.id = items.status_id
                        LEFT JOIN public.rooms ON rooms.id = items.room_id
                        LEFT JOIN public.users ON users.id = items.found_by_id
                        LEFT JOIN public.clients ON clients.id = items.client_id
                        LEFT JOIN public.shipment ON shipment.item_id = items.id
                    WHERE items.id = '{id}'
                    """)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No items to show")
    return item

@router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_item(id: UUID, user: str = Depends(get_current_user)):
    
    #TODO Queries to models
    deleted_item = query(f""" SELECT * FROM items WHERE id = '{id}'""")
    deleted_item = Item(**deleted_item)

    if not deleted_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id: {id} does not exist")
    if deleted_item.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not allowed to perform this cation")
    deleted_item = query(f""" DELETE FROM items WHERE id = '{id}' RETURNING *""")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_item(id: UUID, item: ItemUpdate, user: UserDB = Depends(get_current_user)):
    updated_item = query(f""" SELECT * FROM items WHERE id = '{id}'""")
    updated_item = Item(**updated_item)
    if not updated_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id: {id} does not exist")
    if updated_item.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not allowed to perform this action")
    updated_item = query(f""" UPDATE items SET 
                            image_url = '{item.image_url}', description = '{item.description}', weight = '{item.weight}', room_id = '{item.room_id}', 
                            category_id = '{item.category_id}', found_date = '{item.found_date}', found_by_id = '{item.found_by_id}', updated_at = NOW() 
                            WHERE id = '{id}' RETURNING *""")
    if item.booking or item.client_email:
        if item.client_id:
            new_client = query(f"""UPDATE clients SET
                                hotel_id = '{user.hotel_id}', room_id = '{item.room_id}', email = '{item.client_email}', 
                                phone_number = '{item.client_phone_number}', name = '{item.client_name}', booking = '{item.booking}'
                                WHERE id = '{item.client_id}'
                                RETURNING *""")
        else:
            new_client = query(f"""INSERT INTO clients 
                        (hotel_id, room_id, email, phone_number, name, booking) 
                        VALUES ('{user.hotel_id}', '{item.room_id}', '{item.client_email}', '{item.client_phone_number}', '{item.client_name}', '{item.booking}') RETURNING *""")

            query(f"""UPDATE items SET client_id = '{new_client['id']}' WHERE id = '{updated_item['id']}' RETURNING *""")

    return updated_item