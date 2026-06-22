from fastapi import APIRouter
from app.db.database import get_connection

router = APIRouter()


@router.post("/charge")
def charge_payment(user_id: int, amount: float, card_number: str, cvv: str):

    # Bug 1: Sensitive data logged — card number and CVV in logs
    print(f"Charging user {user_id}: amount={amount}, card={card_number}, cvv={cvv}")

    # Bug 2: No input validation — negative amounts accepted
    # Bug 3: No idempotency — double charging possible if called twice

    conn = get_connection()

    # Bug 4: SQL injection via f-string
    query = f"INSERT INTO orders (user_id, product, amount, status) VALUES ({user_id}, 'charge', {amount}, 'completed')"
    conn.execute(query)
    conn.commit()

    return {"status": "charged", "amount": amount}


@router.get("/history/{user_id}")
def payment_history(user_id: str):
    conn = get_connection()

    # Bug 5: SQL injection
    query = f"SELECT * FROM orders WHERE user_id = {user_id}"
    results = conn.execute(query).fetchall()

    return {"history": results}


@router.post("/refund")
def refund(order_id: int, amount: float):

    # Bug 6: No check if order exists before refund
    # Bug 7: No check if already refunded — double refund possible
    # Bug 8: No amount validation — can refund more than charged

    conn = get_connection()
    query = f"UPDATE orders SET status='refunded' WHERE id={order_id}"
    conn.execute(query)
    conn.commit()

    return {"status": "refunded", "amount": amount}
