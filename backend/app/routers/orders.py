from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest
from app.services.notification_service import NotificationService
from fastapi import APIRouter, status, HTTPException
from uuid import uuid4 
from typing import Dict 

router = APIRouter()

notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.
orders_store: Dict[str, CreateOrderResponse] = {}   #In-memory storage for orders in a dictionary. However, orders disappear when application restarts.

@router.post("/orders", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order_request: CreateOrderRequest) -> CreateOrderResponse:
    """This is the endpoint for creating an order. It generates a notification when an order is created. key endpoint for SR1. Updated in SR2 as it now stores in memory.
    """
    order_id = str(uuid4())     #Generates a unique order ID using uuid4.
    
    order = CreateOrderResponse(
        order_id = order_id,
        user_id = order_request.user_id,
        restaurant_id = order_request.restaurant_id,
        items = order_request.items,
        status = "Created"
    )
    
    orders_store[order.order_id] = order     #Store the order in the in-memory orders_store dictionary.
    
    #Generate a notification for the order creation event.
    notification.create_order_created_notification(user_id = order_request.user_id, order_id = order.order_id)
    
    return order

@router.patch("/orders/{order_id}/status", response_model = CreateOrderResponse)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
    #this updated status of existing order and generates a notif when status changes. Essential for SR2.
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #404 - not found if order ID does not exist in the in-memory store.
    
    order = orders_store[order_id]
    
    old_status = order.status
    new_status = status_request.status
    
    if old_status == new_status:
        raise HTTPException(status_code = 400, detail = "Order status remains unchanged.")     
    
    order.status = new_status     #Update the order status in the in-memory store.
    orders_store[order_id] = order     #Save the updated order back to the in-memory store.
        
    #Now generate a notification for the order status change event.
    notification.create_order_status_changed_notification(
        user_id = order.user_id,
        order_id = order.order_id,
        old_status = old_status,
        new_status = new_status
    )
    
    return order