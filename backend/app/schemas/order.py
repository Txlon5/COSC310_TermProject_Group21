from pydantic import BaseModel, Field
from typing import List

class CreateOrderRequest(BaseModel):
    """SR1 only cares about notification being generated when an order is created.
        This is the input model for orer creation. 
    """
    user_id: str = Field(..., min_length = 1)
    restaurant_id: str = Field(..., min_length = 1)
    items: List[str] = Field(..., min_items = 1)
    
class CreateOrderResponse(BaseModel):
    """This is the output model for order creation. 
        This returns response after order creation.
    """
    order_id: str
    user_id: str
    restaurant_id: str
    items: List[str]
    status: str