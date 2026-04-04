from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    role: str="user"

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None