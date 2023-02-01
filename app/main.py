

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import time


from app.routes import (
    rt_items,
    rt_users,
    rt_auth,
    rt_roles,
    rt_images,
    rt_categories)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# uvicorn app.main:app --reload
# pip3 freeze > requirements.txt
app.include_router(rt_items.router)
app.include_router(rt_users.router)
app.include_router(rt_auth.router)
app.include_router(rt_roles.router)
app.include_router(rt_images.router)
app.include_router(rt_categories.router)

@app.get("/")
def root():
    return {"message": "Hello World"}


