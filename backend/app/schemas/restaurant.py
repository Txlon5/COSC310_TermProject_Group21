from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    id: int
    name: str = Field(..., min_length=1)


class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1)