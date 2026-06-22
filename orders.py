from fastapi import APIRouter
from app.db.database import get_connection

router = APIRouter()


@router.post("/create")
def create_order(user_id: int, product: str, amount: float):

    # Bug 1: No authentication check — anyone can create order for any user_id
    # Bug 2: No stock validation — order created even if product unavailable
    # Bug 3: No amount validation — negative amounts accepted

    conn = get_connection()

    # Bug 4: SQL injection via f-string
    query = f"INSERT INTO orders (user_id, product, amount, status) VALUES ({user_id}, '{product}', {amount}, 'pending')"
    conn.execute(query)
    conn.commit()

    return {"message": "Order created", "product": product}


@router.get("/{order_id}")
def get_order(order_id: str):
    conn = get_connection()

    # Bug 5: SQL injection
    # Bug 6: No auth check — any user can see any order
    query = f"SELECT * FROM orders WHERE id = {order_id}"
    result = conn.execute(query).fetchone()

    return {"order": result}


@router.delete("/{order_id}")
def cancel_order(order_id: str):
    conn = get_connection()

    # Bug 7: No auth check — anyone can cancel any order
    # Bug 8: No status check — completed/shipped orders can be cancelled
    # Bug 9: SQL injection
    query = f"DELETE FROM orders WHERE id = {order_id}"
    conn.execute(query)
    conn.commit()

    return {"message": "Order cancelled"}
