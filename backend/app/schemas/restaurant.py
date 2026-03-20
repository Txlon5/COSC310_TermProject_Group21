from pydantic import BaseModel
from typing import List, Union

class Restaurant(BaseModel):
    restaurant_id: str
    restaurant_name: str
    tags: List[str] = []

class RestaurantCreate(BaseModel):
    restaurant_name: str
    tags: List[str] = []

class RestaurantUpdate(BaseModel):
    restaurant_name : str
    tags: List[str] = []

# Represents a single menu item returned to the client
class MenuItemOut(BaseModel):
    menuItemId: int
    name: str
    price: float
    category: str

# Represents a restaurant returned to the client
class RestaurantOut(BaseModel):
    restaurant_id: int
    restaurant_name: str
    tags: List[str]
    isOpen: bool
    menuItems: List[MenuItemOut]