from pydantic import BaseModel

class Menu(BaseModel):
    id: int
    restaurant_id: int
    name: str
    price: float