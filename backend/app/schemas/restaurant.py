from pydantic import BaseModel
from typing import List, Union

class Restaurant(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    category: str
    tags: List[str] = []

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str
    tags: List[str] = []

class RestaurantUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    category:str
    tags: List[str] = []

# Represents a single menu item returned to the client
class MenuItemOut(BaseModel):
    menuItemId: int
    name: str
    price: float
    category: str

# Represents a restaurant returned to the client
class RestaurantOut(BaseModel):
    restaurantId: Union[str, int]
    name: str
    tags: List[str]
    isOpen: bool
    menuItems: List[MenuItemOut]
