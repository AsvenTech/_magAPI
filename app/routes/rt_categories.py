from fastapi import Response, status, HTTPException, APIRouter, Depends
from typing import List, Union
from app.schemas import Item, CategoryDetail, CategoryCreate,ListedCategories, UserDB, ItemUpdate
from app.utils.u_db import query
from app.utils.u_auth import get_current_user, get_user
from uuid import UUID

router = APIRouter(prefix="/categories", tags=["Categories"],)

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=CategoryDetail)
def create_category(category: CategoryCreate, user: UserDB = Depends(get_current_user)):
    
    max_position =  query("""SELECT MAX(position) FROM public.categories""")
    new_category = query(f"""INSERT INTO categories 
                        (name, default_weight, icon_url, description, position) 
                        VALUES ('{category.name}', '{category.default_weight}', '{category.icon_url}','{category.description}',{max_position['max']+1}) RETURNING *""")
    
    
    return new_category

@router.get("/", response_model=List[ListedCategories])
def get_categories(user: UserDB = Depends(get_current_user)):

    categories = query(f"""SELECT * FROM public.categories as ct
                        WHERE live = 'true'
                        ORDER BY ct.position ASC    
                        """)
    if isinstance(categories, dict):
        categories = [categories]
    if not categories:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No categories to show")
    return categories

@router.get("/{id}", response_model=CategoryDetail)
def get_category(id: UUID):
    category = query(f""" SELECT * FROM public.categories as ct
                    WHERE ct.id = '{id}'
                    """)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No categories to show")
    return category

@router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_category(id: UUID, user: str = Depends(get_current_user)):
    
    #CHECK IF CATEGORY EXISTS
    deleted_category = query(f""" SELECT * FROM categories WHERE id = '{id}'""")
    if not deleted_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {id} does not exist")

    deleted_category = CategoryDetail(**deleted_category)

    #DELETE CATEGORY
    query(f""" DELETE FROM categories WHERE id = '{id}' RETURNING *""")

    #UPDATE POSITIONS
    query(f"""UPDATE categories SET position = position - 1 WHERE position > {deleted_category.position} RETURNING *""")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_category(id: UUID, category: CategoryCreate, user: UserDB = Depends(get_current_user)):
    updated_category = query(f""" SELECT * FROM categories WHERE id = '{id}'""")
    if not updated_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Category with id: {id} does not exist")

    updated_category = CategoryDetail(**updated_category)
    updated_category = query(f""" UPDATE categories SET 
                            name = '{category.name}', default_weight = '{category.default_weight}', icon_url = '{category.icon_url}', description = '{category.description}', updated_at = NOW() 
                            WHERE id = '{id}' RETURNING *""")
    
    return updated_category