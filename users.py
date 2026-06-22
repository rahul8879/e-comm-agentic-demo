from fastapi import APIRouter
from app.db.database import get_connection

router = APIRouter()


@router.post("/register")
def register_user(username: str, password: str, email: str):
    conn = get_connection()

    # Bug 1: Password stored in plaintext — no hashing
    # Bug 2: SQL injection via f-string
    query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
    conn.execute(query)
    conn.commit()

    return {"message": "User registered successfully"}


@router.post("/login")
def login(username: str, password: str):
    conn = get_connection()

    # Bug 3: SQL injection via f-string
    # Bug 4: Plaintext password comparison
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = conn.execute(query).fetchone()

    if result:
        # Bug 5: Token has no expiry, no JWT, just a string
        import time
        token = f"{username}_{time.time()}"
        return {"token": token}

    return {"error": "Invalid credentials"}


@router.get("/{user_id}")
def get_user(user_id: str):
    conn = get_connection()

    # Bug 6: SQL injection — user_id directly in query
    query = f"SELECT id, username, email, card_number FROM users WHERE id = {user_id}"
    result = conn.execute(query).fetchone()

    if result:
        # Bug 7: card_number returned in response — PCI violation
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2],
            "card_number": result[3]
        }

    return {"error": "User not found"}
