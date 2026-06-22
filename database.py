import sqlite3

# Bug 1: No connection pooling — raw sqlite3 used directly
# Bug 2: Global connection — not thread safe
conn = sqlite3.connect("shop.db")


def get_connection():
    # Bug 3: Returns global connection — will break under concurrent requests
    return conn


def init_db():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            card_number TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            amount REAL,
            status TEXT
        )
    """)
    conn.commit()
