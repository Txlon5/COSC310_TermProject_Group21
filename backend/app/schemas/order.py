from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    restaurant_id: str = Field(..., min_length=1)
    items: List[str] = Field(..., min_length=1)
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None


class CreateOrderResponse(BaseModel):
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[str]
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