from pydantic import BaseModel
from typing import List, Optional, Literal


class Order(BaseModel):
    id: int
    user_id: str
    items: List[str]
    total_price: float

    delivery_method: Optional[Literal["delivery", "pickup"]] = None
    delivery_address: Optional[str] = None
    pickup_location: Optional[str] = None
    assigned_driver: Optional[str] = None

    status: str = "created"
