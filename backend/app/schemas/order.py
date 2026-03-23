from enum import Enum
from app.schemas.delivery import DeliveryType, DeliveryStatus
from app.schemas.item import ItemBase
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# One item inside an order request/response
class OrderItem(ItemBase):
    
    name:str
    price: float
    quantity: int 

# Unified CreateOrderRequest
class CreateOrderRequest(BaseModel):
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    status: DeliveryStatus = DeliveryStatus.created
    delivery_method: DeliveryType = DeliveryType.delivery
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

# Order Object - [Temp here]
class Order(BaseModel):
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    total_price: Optional[float] = None
    status: Optional[DeliveryStatus]
    delivery_method: Optional[DeliveryType] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    assigned_driver: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime]
    

# Response returned after creating/retrieving an order
class OrderOut(BaseModel):
    order_id: int
    restaurant_id: str
    items: List[OrderItem]

class CreateOrderResponse(BaseModel):
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    status: DeliveryStatus = DeliveryStatus.created
    total_price: float = 0 
    delivery_method: DeliveryType = DeliveryType.delivery
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
    status: DeliveryStatus

class DeliveryInfoUpdateRequest(BaseModel):
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

class DeliveryInfoResponse(BaseModel):
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    status: str = Field(..., min_length=1)
