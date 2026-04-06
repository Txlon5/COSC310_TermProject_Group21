import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.repositories.auth_repository import load_all, save_all
from app.schemas.auth import ActionToken, ActionTokenType

TOKEN_EXPIRY_MINUTES = 30


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
        type=token_type,
        created_at=datetime.now(),
        used=False
    )

    # Save action token and return it
    tokens.append(new_token.model_dump(mode="json"))
    save_all(tokens)
    return new_token


def get_action_token_by_id(token_id: str) -> ActionToken:
    # Fetch token values
    tokens = load_all()

    # Find token associated with token_id
    for t in tokens:
        if t.get("id") == token_id:
            return ActionToken(**t)
    raise HTTPException(status_code=404, detail=f"Token '{token_id}' not found")


def is_action_token_valid(token_id: str) -> bool:
    # Fetch token associated with token_id
    token = get_action_token_by_id(token_id)

    # Check if token used
    if not token.used:
        # Calculate time expiry from created time
        expiry = token.created_at + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        # Check if token is expired
        if datetime.now() < expiry:
            # Token valid
            return True

    # Token invalid
    return False


def use_action_token(token_id: str) -> None:
    """
    Marks an action token as used
    Raises 404 if token not found
    """
    # Fetch token values
    tokens = load_all()

    # Find token associated with token_id
    for idx, t in enumerate(tokens):
        if t.get("id") == token_id:
            t["used"] = True
            tokens[idx] = t
            save_all(tokens)
            return
    raise HTTPException(status_code=404, detail=f"Token '{token_id}' not found")