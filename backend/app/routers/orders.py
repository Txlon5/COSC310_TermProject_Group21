from typing import List 
from app.schemas.order import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest, DeliveryInfoUpdateRequest, Order, OrderItem
from app.services.orders_service import OrdersService
from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.user import User
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


# Feat4-SR2, updated endpoint according to Siam and Omarion's work regarding order updates
# Update Order Information
@router.put("/{order_id}", response_model=CreateOrderResponse)
def update_order(order_id: str, items: List[OrderItem]) -> Order:
    return order_service.update_order_info(order_id, items)