from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItem(BaseModel):
    menuItemId: int
    name: str
    price: float
    quantity: int = Field(..., ge=1)

class Cart(BaseModel):
    user_id: str
    restaurant_id: str
    items: List[CartItem] = Field(default_factory=list)
    subtotal: float = 0.0
    created_at: datetime
    updated_at: datetime

class CartCheckoutRequest(BaseModel):
    user_id: str
    card_id: str
    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    
class AddCartItemRequest(BaseModel):
    user_id: str
    restaurant_id: str
    menu_item_id: int
    quantity: int = Field(..., ge=1)
    
class UpdateCartItemRequest(BaseModel):
    user_id: str
    restaurant_id: str
    menu_item_id: int
    quantity: int = Field(..., ge=0)