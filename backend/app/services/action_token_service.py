import uuid
from datetime import datetime
from fastapi import HTTPException
from app.repositories.auth_repository import load_all, save_all
from app.schemas.auth import ActionToken, ActionTokenType


def create_action_token(token_type: ActionTokenType, user_id: str) -> ActionToken:
    """
    Creates a new action token
    Returns an action token on success
    """
    # Fetch token values
    tokens = load_all()

    # Create ActionToken
    new_token = ActionToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=ActionTokenType.reset,
        created_at=datetime.now(),
        used=False,
    )

    # Save action token and return it
    tokens.append(new_token.model_dump())
    save_all(tokens)
    return new_token

def get_action_token_by_id(token_id: str):
    # Fetch token values
    tokens = load_all()

    # Find token associated with token_id
    for t in tokens:
        if t.get("id") == token_id:
            return ActionToken(**t)
    raise HTTPException(status_code=404, detail=f"Token '{token_id}' not found")


