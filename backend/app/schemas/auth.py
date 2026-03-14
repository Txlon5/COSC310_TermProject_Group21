from pydantic import BaseModel, EmailStr, Field
from typing import List

# Login Token
class Token(BaseModel):
    access_token: str
    token_type: str