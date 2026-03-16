from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

class Restaurant(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class RestaurantUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class MenuItemOut(BaseModel):
    menuItemId: int
    name: str
    price: float
    category: str

class RestaurantOut(BaseModel):
    restaurantId: int
    name: str
    tags: List[str]
    isOpen: bool
    menuItems: List[MenuItemOut]