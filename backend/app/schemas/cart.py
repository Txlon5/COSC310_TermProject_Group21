from pydantic import BaseModel, Field
from typing import List
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
    created_at: datetime
    updated_at: datetime
