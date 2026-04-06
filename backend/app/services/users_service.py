import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.user import User, UserCreate, UserUpdate
from app.auth.password_utils import PasswordHandler
from app.schemas.user_validator import UserValidator
from app.repositories.users_repo import load_all, save_all
from app.schemas.auth import ActionTokenType
from app.services.action_token_service import create_action_token

def list_users() -> List[User]:
    """
    Returns list of all users
    """
    return [User(**it) for it in load_all()]

def create_user(payload: UserCreate) -> User:
    """
    Creates a new user
    Returns the new user on success
    Raises 422 if email or password is invalid
    Raises 409 if email is already registered
    """
    # Fetch user values
    users = load_all()
    new_id = str(uuid.uuid4())
    new_name = payload.name.strip()
    new_email=payload.email.strip()
    new_plain_password=payload.password.strip()
    new_role="user"

    # User input validation
    if not UserValidator.is_valid_email(new_email):
        raise HTTPException(status_code=422, detail="Invalid email format.")
    if not UserValidator.is_valid_password(new_plain_password):
        raise HTTPException(status_code=422, detail="Password must at minimum 8 characters, have 1 capital and 1 special character.")
    if not UserValidator.is_valid_role(new_role):
        raise HTTPException(status_code=422, detail="Role must be either user or admin.")
    
    # User conflict validation
    if any(it.get("id") == new_id for it in users):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    check_email_collision(new_email, new_id) # Check if email is already registered

    # Create User
    new_user = User(
        id=new_id,
        name=new_name,
        email=new_email,
        password=PasswordHandler.hash_password(new_plain_password),
        role=new_role,
    )
    users.append(new_user.model_dump())
    save_all(users)

    # Generate verify token and send email
    token = create_action_token(ActionTokenType.verify, new_user.id)
    # send verify email - Not done yet

    return new_user

def get_user_by_id(user_id: str) -> User:
    """
    Returns the user matching the userid
    Raises 404 if no user exists
    """
    users = load_all()
    for it in users:
        if it.get("id") == user_id:
            return User(**it)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def get_user_by_email(email: str) -> User:
    """
    Returns the user matching the email
    Raises 422 if email
    Raises 404 if no user exists
    """
    # User input validation
    if not UserValidator.is_valid_email(email):
        raise HTTPException(status_code=422, detail="Invalid email format.")
    
    # Fetch users and search user associated with email
    users = load_all()
    for it in users:
        if it.get("email") == email:
            return User(**it)
    raise HTTPException(status_code=404, detail=f"User '{email}' not found")

def update_user(user_id: str, payload: UserUpdate) -> User:
    """
    Updates the user matching the userid
    Returns the updated user on success
    Raises 422 if email or password is invalid
    Raises 409 if the new email already exists
    Raises 404 if no user exists
    """
    users = load_all()
    for idx, it in enumerate(users):
        if it.get("id") == user_id:

            # Fetch updated values
            # Name field
            if payload.name is not None:
                new_name = payload.name.strip() 
            else: 
                new_name = it.get("name")

            # Password field
            if payload.password is not None:
                new_password = payload.password.strip()
                # User input validation
                if not UserValidator.is_valid_password(str(new_password)):
                    raise HTTPException(status_code=422, detail="Password must at minimum 8 characters, have 1 capital and 1 special character.")
            else: 
                new_password = it.get("password")

            # Email field
            if payload.email is not None:
                new_email = payload.email.strip()
                # User input validation
                if not UserValidator.is_valid_email(str(new_email)):
                    raise HTTPException(status_code=422, detail="Invalid email format.")
            else: 
                new_email = it.get("email")
            
            # Conflict checks
            check_email_collision(str(new_email), user_id)

            # Fetch role or set to default if none
            user_role = it.get("role", "user")

            # Create updated user object
            updated = User(
                id=user_id,
                name=str(new_name),
                email=str(new_email),
                password=PasswordHandler.hash_password(str(new_password)),
                role=user_role
            )
            
            # Store updated user information
            users[idx] = updated.model_dump(mode='json')
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    """
    Deletes the user matching the given userid
    Raises 404 if no user exists
    """
    users = load_all()
    new_users = []

    # Search user list
    for it in users:
        # Check user is associated with user_id
        if it.get("id") != user_id:
            new_users.append(it)

    # Check if new user list does not contain user
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    # Save new user list
    save_all(new_users)

def login_user (email:str, password: str) -> User:
    """
    Login the user matching the given userid
    Raises 422 if email or password is invalid
    Raises 401 if input password does not match stored password
    """
    # User input validation
    if not UserValidator.is_valid_email(email):
        raise HTTPException(status_code=422, detail="Invalid email format.")
    if not UserValidator.is_valid_password(password):
        raise HTTPException(status_code=422, detail="Password must at minimum 8 characters, have 1 capital and 1 special character.")

    # Fetch user
    user = get_user_by_email(email)

    # Fetch hash password
    hash_password = user.password
    
    # Validate password related to user
    if not (PasswordHandler.verify_password(password, hash_password)):
        # If invalid raise issue for invalid credentials
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return user

def verify_user(user_id: str) -> None:
    """
    Marks the user matching the userid as verified
    Raises 404 if no user exists.
    """
    users = load_all()
    for idx, it in enumerate(users):
        if it.get("id") == user_id:
            it["is_verified"] = True
            users[idx] = it
            save_all(users)
            return
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")


# Helper Functions

# Email Collision Check
def check_email_collision(email: str, ignore_id: str):
    """
    Raises 409 if the email already exists
    Ignores the user with ignore_id, meant to help with a user updating their own info
    """
    users = load_all()
    for it in users:
        if it.get("email") == email and it.get("id") != ignore_id:
            raise HTTPException(status_code=409, detail="Conflict: Email exists already.")
