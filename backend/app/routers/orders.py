from backend.app.schemas.order import CreateOrderRequest, CreateOrderResponse
from backend.app.services.notification_service import NotificationService

from fastapi import APIRouter, status
from uuid import uuid4 

router = APIRouter()

notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.

@router.post("/orders", response_model = CreateOrderResponse, status_code = status.HTTP_201_CREATED)
def create_order(order_request: CreateOrderRequest) -> CreateOrderResponse:
    """This is the endpoint for creating an order. It generates a notification when an order is created. key endpoint for SR1. **Orders not saved anywhere since no database.
    """
    order_id = str(uuid4())     #Generates a unique order ID using uuid4.
    
    order = CreateOrderResponse(
        order_id = order_id,
        user_id = order_request.user_id,
        restaurant_id = order_request.restaurant_id,
        items = order_request.items,
        status = "Created"
    )
    
    #Generate a notification for the order creation event.
    notification.create_order_created_notification(user_id = order_request.user_id, order_id = order.order_id)
    
    return order