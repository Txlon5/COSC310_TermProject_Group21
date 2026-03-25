from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.schemas.menu import MenuItem
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest, DeliveryInfoUpdateRequest, Order, OrderItem
from app.services.orders_service import OrdersService
from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.user import User
from uuid import uuid4
from app.auth.token_utils import get_current_user
 
router = APIRouter(prefix = "/orders", tags = ["Orders"])
order_service = OrdersService()

# Create Order
@router.post("", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order: CreateOrderRequest) -> CreateOrderResponse:
    return order_service.create_order(order)

# Get All Orders
@router.get("/", response_model=List[Order])
def get_orders() -> List[Order]:
    """Retrieves all stored orders."""
    return order_service.list_orders()

# Get Order By Id
@router.get("/{order_id}", response_model=Order, dependencies=[Depends(get_current_user)])
def get_order_by_id(order_id: str, current_user: User = Depends(get_current_user)) -> Order:
    """Retrieves a stored order by its ID. Performs security check in function before return"""
    return order_service.get_order_by_id(order_id, current_user)

# Update Order Status
@router.patch("/{order_id}/status", response_model = Order)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> Order:
    return order_service.update_order_status(order_id, status_request)

# Get all Orders by User Id
@router.get("/history/{user_id}", response_model = List[Order])
def get_past_order_history(user_id: str, current_user: User = Depends(get_current_user)) -> List[Order]:
    #The authenticated user must match the requested user id. SR3 security check.
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to perform this action.") 
    return order_service.get_order_history_by_user_id(user_id)

# Update Order Delivery Status
@router.put("/{order_id}/delivery", response_model=Order)
def update_delivery_info(order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> Order:
    return order_service.assign_delivery_info(order_id, delivery_request)


<<<<<<< HEAD

@router.get("/{order_id}", response_model=CreateOrderResponse)
def get_order(order_id: str) -> CreateOrderResponse:
    """Retrieves a stored order by its ID."""
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")

    return orders_store[order_id]

@router.patch("/{order_id}/status", response_model = CreateOrderResponse)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
    #this updated status of existing order and generates a notif when status changes. Essential for SR2.
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #404 - not found if order ID does not exist in the in-memory store.
    
    order = orders_store[order_id]
    
    old_status = order.status
    new_status = status_request.status
    
     # Prevent same status update
    if old_status == new_status:
        raise HTTPException(status_code = 400, detail = "Order status remains unchanged.")  

    if order.delivery_method == "pickup":
        allowed_next_statuses = PICKUP_STATUS_TRANSITIONS.get(old_status, [])
    else:
        allowed_next_statuses = DELIVERY_STATUS_TRANSITIONS.get(old_status, [])

    if new_status not in allowed_next_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status transition from '{old_status}' to '{new_status}'.")

             
    
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

@router.put("/{order_id}/delivery", response_model=CreateOrderResponse)
def assign_delivery_info(order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
    #Updates delivery or pickup information for an order.
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")

    order = orders_store[order_id]

    order.delivery_method = delivery_request.delivery_method
    order.delivery_address = delivery_request.delivery_address
    order.pickup_location = delivery_request.pickup_location
    order.updated_at = datetime.now(timezone.utc)

    orders_store[order_id] = order
    return order
=======
# Feat4-SR2, updated endpoint according to Siam and Omarion's work regarding order updates
# Update Order Information
@router.put("/{order_id}", response_model=CreateOrderResponse)
def update_order(order_id: str, items: List[OrderItem]) -> Order:
    return order_service.update_order_info(order_id, items)
>>>>>>> feat-6-sr1-subtotal
