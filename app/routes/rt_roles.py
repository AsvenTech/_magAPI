from fastapi import APIRouter, HTTPException, status, Depends, Response
from uuid import UUID

from app.utils.u_db import query
from app.utils.u_auth import get_current_user
from app.schemas import UserDB, RoleCreate, Role

router = APIRouter(prefix="/roles", tags=["roles"],)

@router.get("/")
def get_roles():
    roles = query("""SELECT r.id, r.name, COUNT(rp.permission_id) as num_permissions
                    FROM public.roles r
                    LEFT JOIN public.role_permissions rp ON rp.role_id = r.id
                    GROUP BY r.id, r.name""")
    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No roles to show")
    return roles

@router.get("/{id}")
def get_role(id: UUID):
    role = query(f"""SELECT r.id, r.name, COUNT(rp.permission_id) as num_permissions
                    FROM public.roles r
                    LEFT JOIN public.role_permissions rp ON rp.role_id = r.id
                    WHERE r.id = '{id}'
                    GROUP BY r.id, r.name""")
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No roles to show")
    
    permissions = query(f"""SELECT
                                p.id as permission_id,
                                p.name as permission_name
                            FROM public.roles r
                            JOIN public.role_permissions rp ON rp.role_id = r.id
                            JOIN public.permissions p ON rp.permission_id = p.id
                            WHERE r.id = '{id}';""")
    return permissions

@router.post("/",status_code= status.HTTP_201_CREATED)
def create_role(role: RoleCreate, user: UserDB = Depends(get_current_user)):
    new_role = query(f"""INSERT INTO roles (name, hotel_id) VALUES ('{role.name}', '{user.hotel_id}') RETURNING id""")
    
    for permission_id in role.permissions:
        query(f"INSERT INTO role_permissions (role_id, permission_id) VALUES ('{new_role['id']}', '{permission_id}') RETURNING *")
    return role

@router.delete("/{id}")
def delete_role(id: UUID, user: str = Depends(get_current_user)):
    deleted_role = query(f""" SELECT * FROM roles WHERE id = '{id}'""")
    deleted_role = Role(**deleted_role)

    if not deleted_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with id: {id} does not exist")
    
    deleted_item = query(f""" DELETE FROM roles WHERE id = '{id}' RETURNING *""")
    # query("""UPDATE users
    #             SET role_id = NULL
    #             WHERE role_id IN (SELECT id FROM roles WHERE name = 'Deleted Role');""")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_role(id: UUID, role: RoleCreate, user: UserDB = Depends(get_current_user)):
    updated_role = query(f""" SELECT * FROM items WHERE id = '{id}'""")
    updated_role = Role(**updated_role)
    if not updated_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id: {id} does not exist")
    
    query(f"""DELETE FROM role_permissions WHERE role_id = {id} RETURNING *""")
    for permission_id in role.permissions:
        query(f"INSERT INTO role_permissions (role_id, permission_id) VALUES ({id},{permission_id})")
    return {"message": "Permissions updated successfully"}
    
