# auth.py
# ⚠️ WARNING: This is intentionally buggy code for CodeSentinel demo purposes only

import sqlite3
import hashlib

# Bug 1: Hardcoded secrets
SECRET_KEY   = "wrwerwr"
ADMIN_PASS   = "admin123"
DB_PASSWORD  = "root1234"

# Bug 2: Weak hashing — MD5 is broken
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# Bug 3: No rate limiting — brute force possible
def login(username: str, password: str) -> dict:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Bug 4: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hash_password(password)}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"status": "success", "token": SECRET_KEY}
    return {"status": "failed"}

# Bug 5: Weak password validation — accepts anything
def register(username: str, password: str) -> dict:
    if len(password) < 3:   # ← 3 chars enough!
        return {"error": "Password too short"}

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Bug 6: No duplicate username check
    cursor.execute(
        f"INSERT INTO users VALUES ('{username}', '{hash_password(password)}')"
    )
    conn.commit()
    conn.close()
    return {"status": "registered"}

# Bug 7: Admin check hardcoded
def is_admin(password: str) -> bool:
    return password == ADMIN_PASS