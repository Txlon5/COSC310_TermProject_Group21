from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user_validator import UserValidator
from app.auth.password_utils import PasswordHandler
from app.auth.token_utils import create_token, decode_token
client = TestClient(app)

# Unit Tests

# Password Hash
def test_hash_password():
    data = PasswordHandler.hash_password("Password123!")
    assert data != "Password123!"                                     # True - Check password is not plain text
    assert data == PasswordHandler.hash_password("Password123!")      # True - Manually hashed password matches

# Token Create + Decode
def test_token_create_decode():
    token = create_token({"sub": "jane.doe@example.com"})
    payload = decode_token(token)
    assert payload.get("sub") == "jane.doe@example.com"
    assert payload.get("exp") is not None


# Integration Tests

# Login - Valid
def test_login_valid():
    # Check that valid login works and returns token and token type
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "Password123!"},
    )
    assert r.status_code == 200

    # Check that returned data contains token and token type
    data = r.json()
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
    assert r.status_code == 422

# Login - Invalid Password
def test_login_invalid_password():
    # Check that invalid password is rejected
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "pass"},
    )
    assert r.status_code == 422

# Login - Incorrect Credentials
def test_login_incorrect_login():
    # Check that incorrect login is rejected
    r = client.post(
        "/auth/login",
        data={"username": "jane.doe@example.com", "password": "Password123?"},
    )
    assert r.status_code == 401
