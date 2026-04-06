# Pulling inspiration from login implementation in the FASTAPI docs
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from app.services.action_token_service import (
    get_action_token_by_id,
    is_action_token_valid,
    use_action_token,
)
from app.services.users_service import verify_user, reset_user_password
from app.schemas.auth import ActionTokenType
from app.services.users_service import get_user_by_id
import jwt

# JWT Token encode variables
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # encryption secret key
ALGORITHM = "HS256"  # encryption algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # how long the token lasts till it expires
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# create login token
def create_token(userdata: dict) -> str:
    """
    Create JWT token with passed through userdata ["sub": "userid"] after user credentials validated
    """
    to_encode = userdata.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# decode token and return payload with user data and expiration time
def decode_token(token: str) -> dict:
    """
    Decode JWT token and return payload with userid and token expiration time
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# return userid of user associated with token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Verify JWT token is valid and return the userid associated with the token
    Raises 401 if token is invalid or expired
    Raises 422 if token data is invalid
    """
    try:
        # Decode token and get userid from token payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userid = payload.get("sub")

        # Verify token payload has valid data
        if userid is None:
            raise HTTPException(status_code=422, detail="Invalid token data.")

        # Get user associated with token
        user = get_user_by_id(userid)
    except jwt.InvalidTokenError:
        # Raise exception if token is invalid or expired
        raise HTTPException(status_code=401, detail="Invalid token.")
    return user


# verify user account with a verify action_token
def verify_account(token_id: str) -> None:
    # Verify token is valid
    if not is_action_token_valid(token_id):
        raise HTTPException(
            status_code=400, detail="Verify Token is invalid or expired."
        )
    # Fetch token
    token = get_action_token_by_id(token_id)
    # Set user to verified
    verify_user(token.user_id)
    # Set token to used
    use_action_token(token_id)


# reset user password with a reset action_token
def reset_account_password(token_id: str, new_password: str) -> None:
    # Verify token is valid
    if not is_action_token_valid(token_id):
        raise HTTPException(
            status_code=400, detail="Reset Token is invalid or expired."
        )
    # Fetch token and verify it is a reset token
    token = get_action_token_by_id(token_id)
    if token.type != ActionTokenType.reset:
        raise HTTPException(status_code=400, detail="Invalid token type.")
    # Reset user password
    reset_user_password(token.user_id, new_password)
    # Set token to used
    use_action_token(token_id)
