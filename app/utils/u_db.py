import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import time

from app.config import settings
psycopg2.extras.register_uuid()

DB_HOST = settings.DB_HOST
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD

def connect():
    while True:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                user=DB_USER, password=DB_PASSWORD, cursor_factory=RealDictCursor)
            print("DB connected!")
            return conn
        except Exception as error:
            print("Connection failed")
            print("Error: ", error)
            time.sleep(3)
            break

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