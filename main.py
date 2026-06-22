from fastapi import FastAPI
from app.routers import users, payments, orders

app = FastAPI(
    title="DummyShop API",
    description="A simple e-commerce API",
    version="0.1.0"
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])


@app.get("/")
def root():
    return {"message": "DummyShop API is running"}
