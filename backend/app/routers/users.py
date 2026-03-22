from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.users_service import list_users, create_user, delete_user, update_user, get_user_by_id, get_user_by_email
from app.auth.token_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

# Get all users
@router.get("", response_model=List[User])
def get_users(current_user: User = Depends(get_current_user)):
    # Check if user authorized, raise exception otherwise
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to fetch users.")
    return list_users()

#simple post the payload (is the body of the request)
@router.post("", response_model=User, status_code=201)
def post_user(payload: UserCreate):
    return create_user(payload)

# Get current user 
@router.get("/self", response_model=User)
def get_self(current_user: User = Depends(get_current_user)):
    return current_user

# Get user by id
@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    # Check if user authorized, raise exception otherwise
    if current_user.id != user_id or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to fetch this user.")
    return get_user_by_id(user_id)

# Get user by email
@router.get("/email/{email}", response_model=User)
def get_user_via_email(email: str, current_user: User = Depends(get_current_user)):
    # Check if user authorized, raise exception otherwise
    if current_user.email != email and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to fetch this user.")
    return get_user_by_email(email)

# Update current user
@router.put("/self", response_model=User)
def put_self(payload: UserUpdate, current_user: User = Depends(get_current_user)):
    return update_user(current_user.id, payload)

# Update existing user by id
@router.put("/{user_id}", response_model=User)
def put_user(user_id: str, payload: UserUpdate, current_user: User = Depends(get_current_user)):
    # Check if user authorized, raise exception otherwise
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user.")
    return update_user(user_id, payload)

# Delete self
@router.delete("/self", status_code=status.HTTP_204_NO_CONTENT)
def remove_self(current_user: User = Depends(get_current_user)):
    delete_user(current_user.id)
    return None

# Delete user by id
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: str, current_user: User = Depends(get_current_user)):
    # Check if user authorized, raise exception otherwise
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this user.")
    delete_user(user_id)
    return None

