# DummyShop API

A simple FastAPI e-commerce backend.

> ⚠️ **This repo is intentionally buggy.**  
> It is used as a target for CodeSentinel — an autonomous code review agent.  
> Do NOT use this code in production.

---

## Project Structure

```
dummy-ecommerce/
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── db/
│   │   └── database.py      ← DB connection (buggy)
│   └── routers/
│       ├── users.py         ← User registration, login, profile
│       ├── payments.py      ← Payment processing
│       └── orders.py        ← Order management
├── requirements.txt
└── README.md
```

---

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs at: `http://localhost:8000/docs`

---

## Intentional Bugs (for CodeSentinel to find)

### users.py
- SQL injection via f-string in register, login, get_user
- Password stored in plaintext — no bcrypt
- Auth token has no expiry — violates team standard
- card_number returned in API response — PCI violation

### payments.py
- card_number and CVV logged via print()
- No idempotency — double charging possible
- No input validation — negative amounts accepted
- SQL injection in payment history and refund

### orders.py
- No authentication check on any endpoint
- SQL injection in create, get, cancel
- No stock validation before creating order
- Completed orders can be cancelled — no status check

### db/database.py
- Global sqlite3 connection — not thread safe
- No connection pooling — violates team standard
- Raw sqlite3 used instead of SQLAlchemy

---

## How to Use With CodeSentinel

1. Fork this repo
2. Make a change (add a bug, or fix one)
3. Raise a PR
4. CodeSentinel reviews the PR automatically

This repo is the **target**.  
CodeSentinel is the **reviewer**.
