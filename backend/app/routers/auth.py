from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import LoginToken, ForgotPasswordRequest, ResetPasswordRequest, ActionTokenType
from app.services.users_service import login_user, get_user_by_email
from app.services.action_token_service import create_action_token
from app.auth.email_utils import send_reset_email
from app.auth.token_utils import create_token, verify_account, reset_account_password

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
    return {"detail": "Account verified successfully."}


# forgot password route - sends a password reset email to the user
@router.post("/forgot-password", status_code=200)
def forgot_password(payload: ForgotPasswordRequest):
    # Fetch user_id matching email
    user = get_user_by_email(payload.email)
    # Generate reset token and send reset email
    token = create_action_token(ActionTokenType.reset, user.id)
    send_reset_email(user.email, token.id)
    return {"detail": "Password reset email sent."}


# reset password route - resets user password using a reset token
@router.post("/reset-password/{token_id}", status_code=200)
def reset_password(token_id: str, payload: ResetPasswordRequest):
    # Reset user password using reset token
    reset_account_password(token_id, payload.password)
    return {"detail": "Password reset successfully."}
