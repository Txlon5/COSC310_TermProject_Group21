from pydantic import BaseModel, Field
from typing import List, Optional

class CreateOrderRequest(BaseModel):
    """SR1 only cares about notification being generated when an order is created.
        This is the input model for order creation. 
    """
    user_id: str = Field(..., min_length = 1)
    restaurant_id: str = Field(..., min_length = 1)
    items: List[str] = Field(..., min_length = 1)
    delivery_method: str =  Optional[str] = None
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
    
class OrderStatusUpdateRequest(BaseModel):
    #This is essential for SR2, because this is the input model for order status update. Keeps validatio consistent
    status: str = Field(..., min_length = 1)