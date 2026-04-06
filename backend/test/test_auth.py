import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app.auth.password_utils import PasswordHandler
from app.auth.token_utils import create_token, decode_token, get_current_user
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.services.users_service import get_user_by_id
client = TestClient(app)


def override_get_current_user_admin():
    return User(
        id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        name="Jane Doe",
        email="jane.doe@example.com",
        password="a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea",
        role="admin",
        is_verified=True,
    )

# Unit Tests

# Password Hash
def test_hash_password():
    # Hash password and check that it is not returned as plain text
    data = PasswordHandler.hash_password("Password123!")
    # Check that returned password is not plain text
    assert data != "Password123!"                                           # True - Check password is not plain text
    # Check that returned hashed password matches manual password hash
    assert data == PasswordHandler.hash_password("Password123!")            # True - Manually hashed password matches

# Token Create + Decode
def test_token_create_decode():
    # Create token with test data
    token = create_token({"sub": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"})
    
    # Decode token and verify payload matches userid and has a expiration time
    payload = decode_token(token)

    # Check that token payload returns correct userid
    assert payload.get("sub") == "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    # Check that token returns an expiration time
    assert payload.get("exp") is not None 

# Get Current User - Valid
def test_get_current_user_valid():
    # Create token with test data
    token = create_token({"sub": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"})

    # Get user associated with token
    user = get_current_user(token)

    # Check returned user data is correct
    assert user.id == "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"
    assert user.email == "jane.doe@example.com"

# Get Current User - Invalid Token
def test_get_current_user_invalid_token():
    # Check exception raised for invalid token data
    with pytest.raises(HTTPException) as r:
        get_current_user("fake-token")
        
    # Check returned code is 401 for invalid token
    assert r.value.status_code == 401

# Get Current User - Malformed Token
def test_get_current_user_malformed_token():
    # Check exception raised for malformed token
    with pytest.raises(HTTPException) as r: 
        token = create_token({"na": "na"})
        get_current_user(token)
        
    # Check returned code is 422 for invalid token
    assert r.value.status_code == 422

# Get Current User - User Not Found
def test_get_current_user_na():
    # Create token for a userid that does not exist
    token = create_token({"sub": "00000000-0000-0000-0000-000000000000"})

    # Catch exception for missing user
    with pytest.raises(HTTPException) as r:
        get_current_user(token)
        
    # Check returned code is 404 for missing user
    assert r.value.status_code == 404


# Integration Tests

# Login - Valid
def test_login_valid():
    # Check that valid login works and returns token and token type
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "Password123!"},
    )
    # Check returned code is 200 for valid login
    assert r.status_code == 200

    # Check that returned data is token and a token type
    data = r.json()
    # Check returned access token is not empty
    assert "access_token" in data
    assert data["access_token"] != ""
    assert data["token_type"] == "bearer"

# Login - Invalid Email
def test_login_invalid_email():
    # Check that invalid email is rejected
    r = client.post(
        "/auth/login",
        data={"username": "userexample.com", "password": "Password123!"},
    )
    # Check returned code is 422 for invalid email
    assert r.status_code == 422

# Login - Invalid Password
def test_login_invalid_password():
    # Check that invalid password is rejected
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "pass"},
    )
    # Check returned code is 422 for invalid password
    assert r.status_code == 422

# Login - Incorrect Credentials
def test_login_incorrect_login():
    # Check that incorrect login is rejected
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "Password123?"},
    )
    # Check returned code is 401 for incorrect login
    assert r.status_code == 401

# Login - Unverified User
def test_login_unverified_user():
    # Create unverified test user
    app.dependency_overrides[get_current_user] = override_get_current_user_admin
    r = client.post("/users/", json={"name": "Unverified", "email": "unverified@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]
    app.dependency_overrides = {}

    # Login without verification
    r = client.post(
        "/auth/login",
        data={"username": "unverified@example.com", "password": "Password123!"},
    )
    # Raises 403 for unverified account
    assert r.status_code == 403
    assert "not verified" in r.json()["detail"].lower()

    # Clean up
    app.dependency_overrides[get_current_user] = override_get_current_user_admin
    client.delete(f"/users/{user_id}")
    app.dependency_overrides = {}

# Login - Verified User
def test_login_verified_user():
    from app.services.action_token_service import create_action_token
    from app.schemas.auth import ActionTokenType
    from app.repositories.auth_repository import load_all, save_all

    # Create test user
    app.dependency_overrides[get_current_user] = override_get_current_user_admin
    r = client.post("/users/", json={"name": "Verified", "email": "verified@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]
    app.dependency_overrides = {}

    # Verify user
    token = create_action_token(ActionTokenType.verify, user_id)
    r = client.get(f"/auth/verify/{token.id}")
    assert r.status_code == 200

    # Login user
    r = client.post(
        "/auth/login",
        data={"username": "verified@example.com", "password": "Password123!"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()

    # Clean up
    app.dependency_overrides[get_current_user] = override_get_current_user_admin
    client.delete(f"/users/{user_id}")
    app.dependency_overrides = {}
    save_all([t for t in load_all() if t.get("id") != token.id])
