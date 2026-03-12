from pydantic import BaseModel
from typing import List, Optional


class Order(BaseModel):
    id: int
    user_id: int
    items: List[str]
    total_price: float

    delivery_method: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    assigned_driver: Optional[str] = None