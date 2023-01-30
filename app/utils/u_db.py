import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import time

psycopg2.extras.register_uuid()


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