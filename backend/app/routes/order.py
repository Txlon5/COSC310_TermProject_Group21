from fastapi import APIRouter
from app.data.orders_data import orders_db

router = APIRouter()


@router.get("/orders")
def get_orders():
    return orders_db