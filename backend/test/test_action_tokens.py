import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.auth import ActionToken, ActionTokenType
from app.schemas.user import User
from app.services.action_token_service import (
    create_action_token,
    get_action_token_by_id,
    is_action_token_valid,
    use_action_token,
)
from app.repositories.auth_repository import load_all, save_all

client = TestClient(app)


# Test Preparation


# Create mock admin for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin",
        is_verified=True,
    )


# Override get_current_user() function to return the mock admin
@pytest.fixture(autouse=True)
def apply_admin_override():
    # Set the override
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Pause to allow test to run with override
    yield
    # Clear the override after test is done
    app.dependency_overrides = {}


# Unit Tests


# Create Action Token - Valid
def test_create_action_token():
    token = create_action_token(
        ActionTokenType.verify, "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    )

    # Check token fields
    assert token.id != ""
    assert token.user_id == "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    assert token.type == ActionTokenType.verify
    assert token.created_at is not None
    assert not token.used

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Get Action Token By ID - Valid
def test_get_action_token_by_id():
    token = create_action_token(
        ActionTokenType.verify, "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    )

    fetched = get_action_token_by_id(token.id)

    # Check fetched token matches created token
    assert fetched.id == token.id
    assert fetched.user_id == token.user_id
    assert fetched.type == token.type

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Get Action Token By ID - Not Found
def test_get_action_token_by_id_na():
    with pytest.raises(HTTPException) as r:
        get_action_token_by_id("00000000-0000-0000-0000-000000000000")

    assert r.value.status_code == 404


# Action Token Valid - Valid
def test_is_action_token_valid():
    token = create_action_token(
        ActionTokenType.verify, "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    )

    # Check token
    assert is_action_token_valid(token.id)

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Action Token Valid - Already Used
def test_is_action_token_valid_used():
    token = create_action_token(
        ActionTokenType.verify, "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    )
    use_action_token(token.id)

    # Check token
    assert not is_action_token_valid(token.id)

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Action Token Valid - Expired
def test_is_action_token_valid_expired():
    # Create a token with created_at to test expiry
    expired_token = ActionToken(
        id="00000000-0000-0000-0000-000000000001",
        user_id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        type=ActionTokenType.verify,
        created_at=datetime.now() - timedelta(minutes=31),
        used=False,
    )
    tokens = load_all()
    tokens.append(expired_token.model_dump(mode="json"))
    save_all(tokens)

    # Check token
    assert not is_action_token_valid(expired_token.id)

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != expired_token.id])


# Action Token Valid - Not Found
def test_is_action_token_valid_na():
    with pytest.raises(HTTPException) as r:
        is_action_token_valid("00000000-0000-0000-0000-000000000000")

    assert r.value.status_code == 404


# Use Action Token - Valid
def test_use_action_token():
    token = create_action_token(
        ActionTokenType.verify, "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    )

    use_action_token(token.id)

    # Check token is used
    assert get_action_token_by_id(token.id).used
    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Use Action Token - Not Found
def test_use_action_token_na():
    with pytest.raises(HTTPException) as r:
        use_action_token("00000000-0000-0000-0000-000000000000")
    assert r.value.status_code == 404


# Integration Tests


# Verify Account - Valid
def test_verify_account():
    # Create a test user
    r = client.post(
        "/users/",
        json={
            "name": "User",
            "email": "verify@example.com",
            "password": "Password123!",
        },
    )
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create a verify token for the test user
    token = create_action_token(ActionTokenType.verify, user_id)

    # Verify user
    r = client.get(f"/auth/verify/{token.id}")
    assert r.status_code == 200

    # Check user is verified
    r = client.get(f"/users/{user_id}")
    assert r.json()["is_verified"]
    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])


# Verify Account - Invalid Token (already used)
def test_verify_account_invalid():
    # Create a test user
    r = client.post(
        "/users/",
        json={
            "name": "User",
            "email": "verify@example.com",
            "password": "Password123!",
        },
    )
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create and use a verify token
    token = create_action_token(ActionTokenType.verify, user_id)
    use_action_token(token.id)

    # Verify user with used token
    r = client.get(f"/auth/verify/{token.id}")
    assert r.status_code == 400
    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])


# Verify Account - Not Found
def test_verify_account_na():
    r = client.get("/auth/verify/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
