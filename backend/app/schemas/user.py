from pydantic import BaseModel
from typing import List

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
    name: str
    email: str
    password: str