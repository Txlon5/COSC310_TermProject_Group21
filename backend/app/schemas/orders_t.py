from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# One item inside an order request/response
class OrderItem(BaseModel):
    menuItemId: int
    quantity: int
    item_name: Optional[str] = None

# Unified CreateOrderRequest
class CreateOrderRequest(BaseModel):
    user_id: Optional[str] = None
    restaurant_id: int = Field(..., alias="restaurant_id")
    items: List[OrderItem] = Field(..., alias="items")
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

# Response returned after creating/retrieving an order
class OrderOut(BaseModel):
    order_id: int
    restaurant_id: int
    items: List[OrderItem]

class CreateOrderResponse(BaseModel):
    order_id: str
    user_id: Optional[str] = None
    restaurant_id: int = Field(..., alias="restaurant_id")
    restaurant_name: Optional[str] = None
    items: List[OrderItem]
    status: str
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class UpdateOrderStatusRequest(BaseModel):
    new_status: str
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None

class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(..., min_length=1)

class DeliveryInfoUpdateRequest(BaseModel):
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

class DeliveryInfoResponse(BaseModel):
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    status: str = Field(..., min_length=1)
