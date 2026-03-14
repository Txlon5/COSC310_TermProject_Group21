# Pulling inspiration from login implementation in the FASTAPI docs
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Header, HTTPException, Depends, status
from app.services.users_service import get_user_by_email
import jwt 

# JWT Token encode variables
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # encryption secret key
ALGORITHM = "HS256" # encryption algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # how long the token lasts till it expires
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# create login token 
def create_token(userdata: dict) -> str:
    '''
    Create JWT token with passed through userdata ["sub": "userid"] after user credentials validated
    '''
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
