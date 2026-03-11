from fastapi import APIRouter, status
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.users_service import list_users, create_user, delete_user, update_user, get_user_by_id

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[User])
def get_users():
    return list_users()

#simple post the payload (is the body of the request)
@router.post("", response_model=User, status_code=201)
def post_user(payload: UserCreate):
    return create_user(payload)

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    return get_user_by_id(user_id)

## We use put here because we are not creating an entirely new user, ie. we keep id the same
@router.put("/{user_id}", response_model=User)
def put_user(user_id: str, payload: UserUpdate):
    return update_user(user_id, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: str):
    delete_user(user_id)
    return None