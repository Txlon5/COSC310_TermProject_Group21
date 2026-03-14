from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.schemas.auth import Token, LoginField
from app.services.users_service import login_user
from app.auth.token_utils import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

# login route - returns JWT token after valid credentials provided
@router.post("/login", response_model=Token)
def login(form_data: LoginField = Depends()):
    # Verify user login is valid or throw exception
    login_user(form_data.username, form_data.password)
    # Pass in username and create authorized JWT token
    token = create_token({"sub": form_data.username})
    # Return valid token to user logging in
    return Token(access_token=token, token_type="bearer")
