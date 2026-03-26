from pydantic import BaseModel, Field
from app.schemas.item import ItemBase


class Menu(BaseModel):
    id: str
    restaurant_id: str
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class MenuCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class MenuItem(ItemBase):
    price: float
    category: str


class CreateMenuItem(BaseModel):
    name: str
    price: float
    category: str


class UpdateMenuItem(BaseModel):
    name: str
    price: float
    category: str
