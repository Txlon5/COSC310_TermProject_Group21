from pydantic import BaseModel, EmailStr, Field
from typing import List

# Login Token
class Token(BaseModel):
    access_token: str
    token_type: str

# Login Field
class LoginField(BaseModel):
    # User email and password fields
    username: EmailStr
    password: str

    # Set login grant type to password and ignore client id and secret
    # Client id and secret set to empty as it is unnecessary for logging in but are required fields in the request
    grant_type: str = "password" 
    client_id: str = ""
    client_secret: str = ""