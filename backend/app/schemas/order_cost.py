from pydantic import BaseModel, Field
from typing import List


class OrderItemRequest(BaseModel):
    # The ID of the menu item the user wants to order
    item_id: str = Field(..., min_length=1)

    # How many of that item the user wants
    quantity: int = Field(..., ge=1)


class SubtotalRequest(BaseModel):
    # The restaurant the order belongs to
    restaurant_id: str = Field(..., min_length=1)

    # The selected items in the order/cart
    items: List[OrderItemRequest] = Field(..., min_length=1)


class SubtotalResponse(BaseModel):
    # Cost of all items before fees/taxes
    subtotal: float