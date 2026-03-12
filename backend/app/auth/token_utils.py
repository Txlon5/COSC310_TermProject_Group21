# Pulling inspiration from login implementation in the FASTAPI docs
# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

# JWT Token encode variables
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # encryption secret key
ALGORITHM = "HS256" # encryption algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # how long the token lasts till it expires
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # route for user login

# create login token 
def create_token(userdata: dict) -> None:
    '''
    Create JWT token with provided userdata ["sub", "username"] after user credentials validated
    '''
    to_encode = userdata.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)