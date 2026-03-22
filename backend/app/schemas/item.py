from pydantic import BaseModel, Field
from typing import Optional

class ItemBase(BaseModel):
    menuItemId: int
    name: str