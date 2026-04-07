from pydantic import BaseModel
from enum import StrEnum
from datetime import datetime

# Login Token
class LoginToken(BaseModel):
    access_token: str
    token_type: str

# ActionToken Types - Reset Password, Verify Account
class ActionTokenType(StrEnum):
    reset = "reset"
    verify = "verify"

# ActionToken
class ActionToken(BaseModel):
    id: str
    user_id: str
    type: ActionTokenType
    created_at: datetime
    used: bool = False

# Forgot Password Request
class ForgotPasswordRequest(BaseModel):
    email: str

# Reset Password Request
class ResetPasswordRequest(BaseModel):
    password: str