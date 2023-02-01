from passlib.context import CryptContext
from app.schemas import UserDB, Token, TokenData
from app.utils.u_db import query
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_permission_ids_for_user(user_id: int) -> List[int]:
    result = query(f"""
        SELECT u.id as user_id, 
            r.id as role_id,
            r.name as role_name,
            p.id as permission_id,
            p.name as permission_name
        FROM public.users u
        JOIN public.roles r ON u.role_id = r.id
        JOIN public.role_permissions rp ON rp.role_id = r.id
        JOIN public.permissions p ON rp.permission_id = p.id
        WHERE u.id = '{user_id}';
    """)
    permission_ids = [row["permission_name"] for row in result]
    #print(permission_ids)
    return permission_ids

def get_user(email: str):
    user = query(f"SELECT * FROM users WHERE email = '{email}'")
    if user:
        user = UserDB(**user)
    else:
        return None
    user.permissions = get_permission_ids_for_user(user.id) 
    return user

def autenticate_user(email, password):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password,user.password):
        return False
    else: 
        return user

def create_access_token(data: dict):
    to_encode = data.copy()

    #TODO: Optional expire delta
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(token: str =Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.email)

    if user is None:
        raise credentials_exception

    return user


