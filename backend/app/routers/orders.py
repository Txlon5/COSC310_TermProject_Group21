from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest
from app.services.notification_service import NotificationService
from fastapi import APIRouter, status, HTTPException, Header, Request
from uuid import uuid4 
import logging
 
router = APIRouter(prefix = "/orders", tags = ["Orders"])

notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.
orders_store: Dict[str, CreateOrderResponse] = {}   #In-memory storage for orders in a dictionary. However, orders disappear when application restarts.

#For SR3, we will be storing unauthorized access attempts
unauthorized_access_log: List[dict] = []
logger = logging.getLogger(__name__)        #creates a python logger for server logs

def validate_access_to_order_history(requested_user_id: str, authenticated_user_id: Optional[str], path: str) -> None:
    
    #Unauthenticated user request rejected
    if authenticated_user_id is None:
        attempt = {"requested_user_id": requested_user_id, "authenticated_user_id": None, "path": path, "timestamp": datetime.now(timezone.utc)}
        unauthorized_access_log.append(attempt)
        logger.warning("Unauthorized attempt: order history access rejected: %s", attempt)
        raise HTTPException(status_code = 401, detail = "Authentication required.")
 
@router.post("", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order_request: CreateOrderRequest) -> CreateOrderResponse:
    """This is the endpoint for creating an order. It generates a notification when an order is created. key endpoint for SR1. Updated in SR2 as it now stores in memory.
    """
    order_id = str(uuid4())     #Generates a unique order ID using uuid4.
    now = datetime.now(timezone.utc)     #records tiem wfor when order is created/updated/delivered
    
    order = CreateOrderResponse(
        order_id = order_id,
        user_id = order_request.user_id,
        restaurant_id = order_request.restaurant_id,
        items = order_request.items,
        status = "Created",
        created_at = now,
        updated_at = now,
        delivered_at = None
    )
    
    orders_store[order.order_id] = order     #Store the order in the in-memory orders_store dictionary.
    
    #Generate a notification for the order creation event.
    notification.create_order_created_notification(user_id = order_request.user_id, order_id = order.order_id)
    
    return order

@router.patch("/{order_id}/status", response_model = CreateOrderResponse)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
    #this updated status of existing order and generates a notif when status changes. Essential for SR2.
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #404 - not found if order ID does not exist in the in-memory store.
    
    order = orders_store[order_id]
    
    old_status = order.status
    new_status = status_request.status
    
    if old_status == new_status:
        raise HTTPException(status_code = 400, detail = "Order status remains unchanged.")     
    
    now = datetime.now(timezone.utc)
    
    order.status = new_status     #Update the order status in the in-memory store.
    order.updated_at = now
    
    if new_status =="Delivered":
        order.delivered_at = now
        
    orders_store[order_id] = order     #Save the updated order back to the in-memory store.
    
        
    #Now generate a notification for the order status change event.
    notification.create_order_status_changed_notification(
        user_id = order.user_id,
        order_id = order.order_id,
        old_status = old_status,
        new_status = new_status
    )
    
    return order

@router.get("/history/{user_id}", response_model = List[CreateOrderResponse])
def get_past_order_history(user_id: str) -> List[CreateOrderResponse]:
    #For a specific order, view all past orders.
    user_orders = [order for order in orders_store.values()      #Reuses current in-memory orders_store, satisfies SR1
                   if order.user_id == user_id]
    return user_orders

@router.get("/history/{user_id}/{order_id}", response_model = CreateOrderResponse)
def get_certain_past_order(user_id: str, order_id: str) -> CreateOrderResponse:
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #Verifies whether the order exists
    
    order = orders_store[order_id]
    
    if order.user_id != user_id:
        raise HTTPException(status_code = 403, detail = "Not authorized to view this order.")       #verfies if order belongs to correct user
    
    return order 