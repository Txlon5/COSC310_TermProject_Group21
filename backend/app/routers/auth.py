from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import LoginToken, ForgotPasswordRequest, ActionTokenType
from app.services.users_service import login_user, get_user_by_email
from app.services.action_token_service import create_action_token
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


# verify account route - marks user as verified using a verify token
@router.get("/verify/{token_id}", status_code=200)
def verify(token_id: str):
    verify_account(token_id)


# forgot password route - sends a password reset email to the user
@router.post("/forgot-password", status_code=200)
def forgot_password(payload: ForgotPasswordRequest):
    # Fetch user_id matching email
    user = get_user_by_email(payload.email)
    # Generate reset token and send reset email
    token = create_action_token(ActionTokenType.reset, user.id)
    # send reset email - Not done yet
