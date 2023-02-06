

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import time
import sentry_sdk

from app.config import settings
from app.routes import (
    rt_items,
    rt_users,
    rt_auth,
    rt_roles,
    rt_images,
    rt_categories)



sentry_sdk.init(
    dsn=settings.SENTRY_DSN,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)

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

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

@app.get("/")
def root():
    return {"message": "Hello World"}


