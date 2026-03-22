from typing import Dict, List, Optional
from datetime import datetime, timezone
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest, DeliveryInfoUpdateRequest, Order
from app.services.orders_service import OrdersService
from app.services.notification_service import NotificationService
from fastapi import APIRouter, status, HTTPException, Header, Request, Body
from uuid import uuid4
import logging 
 
router = APIRouter(prefix = "/orders", tags = ["Orders"])

notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.
orders_store: Dict[str, CreateOrderResponse] = {}   #In-memory storage for orders in a dictionary. However, orders disappear when application restarts.

#For SR3, we will be storing unauthorized access attempts
unauthorized_access_log: List[dict] = []
logger = logging.getLogger(__name__)        #creates a python logger for server logs

def validate_access_to_order_history(requested_user_id: str, authenticated_user_id: Optional[str], path: str) -> None:
    
    #Unauthenticated user requests rejected
    if authenticated_user_id is None:
        attempt = {"requested_user_id": requested_user_id, "authenticated_user_id": None, "path": path, "timestamp": datetime.now(timezone.utc)}
        unauthorized_access_log.append(attempt)
        logger.warning("Unauthorized attempt: order history access rejected: %s", attempt)
        raise HTTPException(status_code = 401, detail = "Authentication required.")
    
    #Accessing other user data requests rejected
    if authenticated_user_id != requested_user_id:
        attempt = {"requested_user_id": requested_user_id, "authenticated_user_id": authenticated_user_id, "path": path, "timestamp": datetime.now(timezone.utc)}
        unauthorized_access_log.append(attempt)
        logger.warning("Unauthorized attempt: forbidden order history access: %s", attempt)
        raise HTTPException(status_code = 403, detail = "Not authorized to access this order history.")
    

@router.post("", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order: CreateOrderRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.create_order_tariq(order)

@router.get("/", response_model=List[Order])
def get_orders() -> List[Order]:
    order_service = OrdersService()
    """Retrieves all stored orders."""
    return order_service.list_orders()

@router.get("/{order_id}", response_model=CreateOrderResponse)
def get_order_by_id(order_id: str) -> CreateOrderResponse:
    """Retrieves a stored order by its ID."""
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")
    return orders_store[order_id]

@router.patch("/{order_id}/status", response_model = CreateOrderResponse)
def update_order_status(order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.update_order_status(order_id, status_request)


@router.get("/history/{user_id}", response_model = List[CreateOrderResponse])
def get_past_order_history(user_id: str, request: Request, x_user_id: Optional[str] = Header(default = None)) -> List[CreateOrderResponse]:
    validate_access_to_order_history(requested_user_id = user_id, authenticated_user_id = x_user_id, path = str(request.url.path))      #The authenticated user must match the requested user id. SR3 security check.
    #For a specific order, view all past orders.
    user_orders = [order for order in orders_store.values()      #Reuses current in-memory orders_store, satisfies SR1
                   if order.user_id == user_id]
    return user_orders

@router.get("/history/{user_id}/{order_id}", response_model = CreateOrderResponse)
def get_certain_past_order(user_id: str, order_id: str, request: Request, x_user_id: Optional[str] = Header(default = None)) -> CreateOrderResponse:
    validate_access_to_order_history(requested_user_id=user_id, authenticated_user_id=x_user_id, path=str(request.url.path))
    if order_id not in orders_store:
        raise HTTPException(status_code = 404, detail = "Order not found.")     #Verifies whether the order exists
    
    order = orders_store[order_id]
    
    if order.user_id != user_id:
        raise HTTPException(status_code = 403, detail = "Not authorized to view this order.")       #verfies if order belongs to correct user
    
    return order 

@router.put("/{order_id}/delivery", response_model=CreateOrderResponse)
def a_delivery_info(order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
    order_service = OrdersService()
    return order_service.assign_delivery_info(order_id, delivery_request)

# newly pulled branch
def assign_delivery_info(order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")

    order = orders_store[order_id]

    order.delivery_method = delivery_request.delivery_method
    order.delivery_address = delivery_request.delivery_address
    order.pickup_location = delivery_request.pickup_location
    order.updated_at = datetime.now(timezone.utc)

    orders_store[order_id] = order
    return order


# Feat4-SR2, updated endpoint according to Siam and Omarion's work regarding order updates
@router.put("/{order_id}", response_model=CreateOrderResponse)
def update_order(order_id: str, items: List[dict] = Body(default=None), restaurant_id: int = None):
    if order_id not in orders_store:
        raise HTTPException(status_code=404, detail="Order not found.")
    order = orders_store[order_id]
    if order.status in ("Delivered", "Picked up"):
        raise HTTPException(status_code=400, detail="Cannot update a completed (Delivered or Picked up) order.")
    if restaurant_id is not None:
        order.restaurant_id = restaurant_id
    if items is not None:
        order.items = items
    order.updated_at = datetime.now(timezone.utc)
    orders_store[order_id] = order
    return order
