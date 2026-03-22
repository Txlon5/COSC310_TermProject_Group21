from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.schemas.menu import MenuItem
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest, DeliveryInfoUpdateRequest, Order, OrderItem
from app.services.orders_service import OrdersService
from app.services.notification_service import NotificationService
from fastapi import APIRouter, status, HTTPException, Header, Request, Body, Depends
from app.schemas.user import User
from uuid import uuid4
from app.auth.token_utils import get_current_user
import logging 
 
router = APIRouter(prefix = "/orders", tags = ["Orders"])

notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.
orders_store: Dict[str, CreateOrderResponse] = {}   #In-memory storage for orders in a dictionary. However, orders disappear when application restarts.


# Create Order
@router.post("", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order: CreateOrderRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.create_order_tariq(order)

# Get All Orders
@router.get("/", response_model=List[Order])
def get_orders() -> List[Order]:
    """Retrieves all stored orders."""
    order_service = OrdersService()
    return order_service.list_orders()

# Get Order By Id
@router.get("/{order_id}", response_model=CreateOrderResponse)
def get_order_by_id(order_id: str) -> CreateOrderResponse:
    """Retrieves a stored order by its ID."""
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")
    return orders_store[order_id]

# Update Order Status
@router.patch("/{order_id}/status", response_model = CreateOrderResponse)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.update_order_status(order_id, status_request)

# Get all Orders by User Id
@router.get("/history/{user_id}", response_model = List[CreateOrderResponse])
def get_past_order_history(user_id: str, current_user: User = Depends(get_current_user)) -> List[CreateOrderResponse]:
    #The authenticated user must match the requested user id. SR3 security check.
    if current_user.id != user_id or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to perform this action.") 
    
    #For a specific order, view all past orders.
    user_orders = [order for order in orders_store.values()      #Reuses current in-memory orders_store, satisfies SR1
                   if order.user_id == user_id]
    return user_orders

# Get Order by User Id and Order Id
@router.get("/history/{user_id}/{order_id}", response_model = CreateOrderResponse)
def get_certain_past_order(user_id: str, order_id: str, current_user: User = Depends(get_current_user)) -> CreateOrderResponse:
    #The authenticated user must match the requested user id. SR3 security check.
    if current_user.id != user_id or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to perform this action.")
    
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #Verifies whether the order exists
    
    order = orders_store[order_id]
    return order 

# Update Order Delivery Status
@router.put("/{order_id}/delivery", response_model=CreateOrderResponse)
def update_delivery_info(order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.assign_delivery_info(order_id, delivery_request)


# Feat4-SR2, updated endpoint according to Siam and Omarion's work regarding order updates
# Update Order Information
@router.put("/{order_id}", response_model=CreateOrderResponse)
def update_order(order_id: str, items: List[OrderItem], restaurant_id: str):
    order_service = OrdersService()
    return order_service.update_order_info(order_id, items, restaurant_id)