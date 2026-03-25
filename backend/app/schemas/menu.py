from pydantic import BaseModel, Field
from app.schemas.item import ItemBase

class Menu(BaseModel):
    id: str
<<<<<<< HEAD
    restaurant_id: int
=======
    restaurant_id: str
>>>>>>> feat-6-sr1-subtotal
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class MenuCreate(BaseModel):
<<<<<<< HEAD
    restaurant_id: str
=======
>>>>>>> feat-6-sr1-subtotal
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)

class MenuItem(ItemBase):
    price: float
    category: str

class CreateMenuItem(BaseModel):
    name: str
    price: float
    category: str
