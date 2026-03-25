from pydantic import BaseModel, Field, field_validator
from typing import List,Optional


class OrderItemRequest(BaseModel):
    # The ID of the menu item the user wants to order
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1)

#Sr1
class SubtotalRequest(BaseModel):
    # The restaurant the order belongs to
    restaurant_id: str = Field(..., min_length=1)
    # The selected items in the order/cart
    items: List[OrderItemRequest] = Field(..., min_length=1)


class SubtotalResponse(BaseModel):
    # Cost of all items before fees/taxes
    subtotal: float

# SR2
class OrderCostRequest(BaseModel):
    restaurant_id: str
    items: List[OrderItemRequest]
    delivery_method: str  # "delivery" or "pickup"

    # NEW (simple location fields)
    delivery_address: Optional[str] = None
    province: Optional[str] = "BC"
    distance_km: Optional[float] = 0

    # distance validation
    @field_validator("distance_km")
    @classmethod
    def validate_distance(cls, v):
        if v is not None and v < 0:
            raise ValueError("distance_km cannot be negative")
        return v

class OrderCostResponse(BaseModel):
    subtotal: float
    delivery_fee: float
    tax: float
    total: float