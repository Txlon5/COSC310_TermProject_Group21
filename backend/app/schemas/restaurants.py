# This file is meant to verify the structure of the restaurant data

from pydantic import BaseModel
from typing import List


# Represents a single menu item returned to the client
class MenuItemOut(BaseModel):
    menuItemId: int
    name: str
    price: float
    category: str

# Represents a restaurant returned to the client
class RestaurantOut(BaseModel):
    restaurant_id: int
    name: str
    tags: str
    isOpen: bool
    menuItems: List[MenuItemOut]