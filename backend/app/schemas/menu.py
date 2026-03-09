from pydantic import BaseModel, Field


class Menu(BaseModel):
    id: int
    restaurant_id: int
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)


class MenuCreate(BaseModel):
    restaurant_id: int
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)