from pydantic import BaseModel
from app.schemas.menu import MenuItem
from typing import List, Optional

# Represents a single menu item returned to the client

class Restaurant(BaseModel):
    restaurant_id: str
    restaurant_name: str
    isOpen: bool
    tags: List[str]
    menuItems: List[MenuItem]

class RestaurantCreate(BaseModel):
    restaurant_name: str
    isOpen: bool = True
    tags: List[str] = []

class RestaurantUpdate(BaseModel):
    restaurant_name: str
    isOpen: Optional[bool] = None
    tags: Optional[List[str]] = None

class RestaurantMinimal(BaseModel):
    restaurant_id: str
    restaurant_name: str
    tags: List[str]