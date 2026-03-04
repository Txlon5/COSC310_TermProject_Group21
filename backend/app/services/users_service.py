import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.user import User, UserCreate, UserUpdate
from repositories.users_repo import load_all, save_all

def list_users() -> List[User]:
    return [User(**it) for it in load_all()]

def create_user(payload: UserCreate) -> User:
    users = load_all()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in users):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_user = User(id=new_id, name=payload.name.strip(), email=payload.email.strip(), password=payload.password.strip())
    users.append(new_user.dict())
    save_all(users)
    return new_user

def get_user_by_id(user_id: str) -> User:
    users = load_all()
    for it in users:
        if it.get("id") == user_id:
            return User(**it)
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def update_user(user_id: str, payload: UserUpdate) -> User:
    users = load_all()
    for idx, it in enumerate(users):
        if it.get("id") == user_id:
            updated = User(
                id=user_id,
                name=payload.name.strip(),
                email=payload.email.strip(),
                password=payload.password.strip(),
            )
            users[idx] = updated.dict()
            save_all(users)
            return updated
    raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

def delete_user(user_id: str) -> None:
    users = load_all()
    new_users = [it for it in users if it.get("id") != user_id]
    if len(new_users) == len(users):
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    save_all(new_users)