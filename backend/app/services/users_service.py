import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.user_validator import UserValidator
from app.repositories.users_repo import load_all, save_all

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
    users = load_all()
    new_id = str(uuid.uuid4())
    new_name = payload.name.strip()
    new_email=payload.email.strip()
    new_plain_password=payload.password.strip()

    # User input validation
    if not UserValidator.is_valid_email(new_email):
        raise HTTPException(status_code=422, detail="Invalid email format.")
    if not UserValidator.is_valid_password(new_plain_password):
        raise HTTPException(status_code=422, detail="Password must at minimum 8 characters, have 1 capital and 1 special character.")
    
    # User conflict validation
    if any(it.get("id") == new_id for it in users):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    check_email_collision(new_email, new_id) # Check if email is already registered

    # Create User
    new_user = User(id=new_id, name=new_name, email=new_email, password=UserValidator.hash_password(new_plain_password))
    users.append(new_user.model_dump())
    save_all(users)
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
    Raises 404 if no user exists
    """
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
            # User input validation
            if not UserValidator.is_valid_email(payload.email.strip()):
                raise HTTPException(status_code=422, detail="Invalid email format.")
            if not UserValidator.is_valid_password(payload.password.strip()):
                raise HTTPException(status_code=422, detail="Password must at minimum 8 characters, have 1 capital and 1 special character.")
            
            # Conflict checks
            check_email_collision(payload.email.strip(), user_id)

            # Create updated user object
            updated = User(
                id=user_id,
                name=payload.name.strip(),
                email=payload.email.strip(),
                password=UserValidator.hash_password(payload.password.strip()),
            )
            
            # Store updated user information
            users[idx] = updated.model_dump()
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    """
    Deletes the user matching the given userid
    Raises 404 if no user exists
    """
    users = load_all()
    new_users = [it for it in users if it.get("id") != user_id]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_all(new_users)

# def login_user (email:str, password: str) -> None:



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