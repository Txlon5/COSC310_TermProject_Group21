from fastapi import APIRouter, HTTPException
from app.data.orders_data import orders_db
from app.schemas.order import UpdateOrderStatusRequest

router = APIRouter()

VALID_STATUSES = ["created", "preparing", "out_for_delivery", "delivered"]


# Returns the full list of orders
@router.get("/orders")
def get_orders():
    return orders_db


# Retrieve a single order and see its status
@router.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders_db if o.id == order_id), None)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


# Update the order status
@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: UpdateOrderStatusRequest):
    order = next((o for o in orders_db if o.id == order_id), None)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status_update.new_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.status = status_update.new_status
    return {
        "message": "Order status updated successfully",
        "order": order
    }