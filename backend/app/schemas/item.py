from pydantic import BaseModel

class ItemBase(BaseModel):
    menuItemId: int
    name: str