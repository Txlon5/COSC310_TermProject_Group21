from pydantic import BaseModel
from typing import List

class Restaurant(BaseModel):
    id: str
    name: str
    category: str
    tags: List[str] = []

class RestaurantCreate(BaseModel):
    name: str
    category: str
    tags: List[str] = []

class RestaurantUpdate(BaseModel):
    name : str
    category:str
    tags: List[str] = []