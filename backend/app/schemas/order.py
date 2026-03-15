from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    """SR1 only cares about notification being generated when an order is created.
        This is the input model for order creation. 
    """
    user_id: str = Field(..., min_length = 1)
    restaurant_id: str = Field(..., min_length = 1)
    items: List[str] = Field(..., min_length = 1)
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

class CreateOrderResponse(BaseModel):
   # This is the output model for order creation. 
        #This returns response after order creation.
    
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[str]
    status: str
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime] = None     #optional, as it returns the time only when an order is delivered.
    
class OrderStatusUpdateRequest(BaseModel):
    """This is essential for SR2, because this is the input model for order status update. Keeps validatio consistent"""
    status: str = Field(..., min_length = 1)

class DeliveryInfoUpdateRequest(BaseModel):
   
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None

class DeliveryInfoResponse(BaseModel):
   
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    
    status: str = Field(..., min_length = 1)
