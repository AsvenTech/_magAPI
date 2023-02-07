from app.utils.u_db import query
from app.utils.u_auth import autenticate_user, create_access_token
from fastapi import Depends, status, HTTPException, APIRouter
from app.schemas import UserLogin, UserDB
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])

############
from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

from app.config import settings


class EmailSchema(BaseModel):
    email: List[EmailStr]

MAIL_USERNAME = settings.MAIL_USERNAME
MAIL_PASSWORD = settings.MAIL_PASSWORD
MAIL_FROM = settings.MAIL_FROM
conf = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_FROM = MAIL_FROM,
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

html = """
<p>Thanks for using Fastapi-mail</p> 
"""


@router.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})  
############

@router.post("/login")
def login(credentials: OAuth2PasswordRequestForm = Depends()):
    #We get username and password
    user = autenticate_user(credentials.username,credentials.password)
    #From here we get full user object from db

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
        )
    acces_token = create_access_token(data = {"email":user.email, "role_id": str(user.role_id)} )
    return {"access_token": acces_token, "token_type": "bearer", "permissions": user.permissions}