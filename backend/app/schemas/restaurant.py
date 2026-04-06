from pydantic import BaseModel, Field, ConfigDict
from app.schemas.menu import MenuItem
from typing import List, Optional

# Represents a single menu item returned to the client

class Restaurant(BaseModel):
    restaurant_id: str
    restaurant_name: str
    isOpen: bool
    opening_time: str
    closing_time: str
    tags: List[str]
    menuItems: List[MenuItem]

class RestaurantCreate(BaseModel):
    restaurant_name: str
    isOpen: bool = True
    opening_time: str
    closing_time: str
    tags: List[str]

class RestaurantUpdate(BaseModel):
    restaurant_name: Optional[str] = None
    isOpen: Optional[bool] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Set FASTAPI docs route example
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "restaurant_name": "",
                "isOpen": True,
                "opening_time": "09:00",
                "closing_time": "21:00",
                "tags": []
            }
        }
    )

class RestaurantMinimal(BaseModel):
    restaurant_id: str
    restaurant_name: str
    tags: List[str]