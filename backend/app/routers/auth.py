from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import LoginToken
from app.services.users_service import login_user
from app.auth.token_utils import create_token, verify_account

router = APIRouter(prefix="/auth", tags=["auth"])


# login route - returns JWT token after valid credentials provided
@router.post("/login", response_model=LoginToken)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify user login is valid or throw exception
    user = login_user(form_data.username, form_data.password)
    # Pass in username and create authorized JWT token
    token = create_token({"sub": user.id})
    # Return valid token to user logging in
    return LoginToken(access_token=token, token_type="bearer")


@router.get("/verify/{token_id}", status_code=200)
def verify(token_id: str):
    verify_account(token_id)
