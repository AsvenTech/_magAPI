from passlib.context import CryptContext

from app.schemas import UserDB
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(email: str):
    user = query(f"SELECT * FROM users WHERE email = '{email}'")
    return UserDB(**user) if user else None

def autenticate_user(email, password):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password,user.password):
        return False
    else: 
        return user

def connect():
    while True:
        try:
            conn = psycopg2.connect(host='localhost', database='forgate',
                user='postgres', password='Tuccetino10.', cursor_factory=RealDictCursor)
            print("DB connected!")
            return conn
        except Exception as error:
            print("Connection failed")
            print("Error: ", error)
            time.sleep(3)

def query(sql,commit=True):
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    sql = cur.fetchall()
    if commit:
        conn.commit()
    if len(sql)==1:
        return sql[0]
    else:
        return sql