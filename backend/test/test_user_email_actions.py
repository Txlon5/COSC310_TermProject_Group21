import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.auth.token_utils import get_current_user
from app.auth.password_utils import PasswordHandler
from app.schemas.auth import ActionTokenType
from app.schemas.user import User
from app.services.action_token_service import create_action_token, use_action_token
from app.services.users_service import reset_user_password
from app.auth.email_utils import send_verification_email, send_reset_email
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

# Reset User Password - Valid
def test_reset_user_password():
    # Create test user
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Reset test user password
    reset_user_password(user_id, "NewPassword123!")

    # Check password was updated
    r = client.get(f"/users/{user_id}")
    assert r.json()["password"] == PasswordHandler.hash_password("NewPassword123!")

    # Clean up test data
    client.delete(f"/users/{user_id}")

# Reset User Password - Invalid Password
def test_reset_user_password_invalid():
    # Create test user and reset token
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]
    token = create_action_token(ActionTokenType.reset, user_id)

    # Reset password with invalid password
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "weak"})
    assert r.status_code == 422

    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])

# Reset User Password - Not Found
def test_reset_user_password_na():
    # Create reset token for invalid user
    token = create_action_token(ActionTokenType.reset, "00000000-0000-0000-0000-000000000000")

    # Reset password for invalid user
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "NewPassword123!"})
    assert r.status_code == 404

    # Clean up test data
    save_all([t for t in load_all() if t.get("id") != token.id])


# Send Verification Email - Valid Link Format
def test_send_verification_email():
    with patch("app.auth.email_utils.send_email") as mock_send:
        send_verification_email("user@example.com", "test-token-id")

        # Check email was sent with correct recipient and token link
        kwargs = mock_send.call_args.kwargs
        assert kwargs["to"] == "user@example.com"                                  # True - correct recipient
        assert "test-token-id" in kwargs["body"]                                   # True - token in body
        assert "localhost:8000/auth/verify/test-token-id" in kwargs["body"]       # True - correct link

# Send Reset Email - Valid Link Format
def test_send_reset_email():
    with patch("app.auth.email_utils.send_email") as mock_send:
        send_reset_email("user@example.com", "test-token-id")

        # Check email was sent with correct recipient and token link
        kwargs = mock_send.call_args.kwargs
        assert kwargs["to"] == "user@example.com"                                  # True - correct recipient
        assert "test-token-id" in kwargs["body"]                                   # True - token in body
        assert "localhost:8000/auth/reset-password/test-token-id" in kwargs["body"]   # True - correct link


# Integration Tests

# Create User - Sends Verification Email
def test_create_user_sends_verification_email():
    with patch("app.services.users_service.send_verification_email") as mock_send:
        r = client.post("/users/", json={"name": "User", "email": "verify@example.com", "password": "Password123!"})
        assert r.status_code == 201

        # Check verification email was sent to the correct address with verify token
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        assert args[0] == "verify@example.com"
        assert args[1] != ""

        # Clean up test data
        client.delete(f"/users/{r.json()['id']}")

# Forgot Password - Valid
def test_forgot_password():
    with patch("app.routers.auth.send_reset_email") as mock_send:
        r = client.post("/auth/forgot-password", json={"email": "jane.doe@example.com"})
        assert r.status_code == 200

        # Check reset email was sent to the correct address with reset token
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        assert args[0] == "jane.doe@example.com"
        assert args[1] != ""

        # Clean up test token
        save_all([])

# Forgot Password - Not Found
def test_forgot_password_na():
    r = client.post("/auth/forgot-password", json={"email": "nobody@example.com"})
    assert r.status_code == 404

# Reset Password - Valid
def test_reset_password():
    # Create test user
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create reset token for test user
    token = create_action_token(ActionTokenType.reset, user_id)

    # Reset password
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "NewPassword123!"})
    assert r.status_code == 200

    # Check password was updated
    r = client.get(f"/users/{user_id}")
    assert r.json()["password"] == PasswordHandler.hash_password("NewPassword123!")

    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])

# Reset Password - Invalid Token (already used)
def test_reset_password_invalid_token():
    # Create a test user
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create and use reset token
    token = create_action_token(ActionTokenType.reset, user_id)
    use_action_token(token.id)

    # Reset password with used token
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "NewPassword123!"})
    assert r.status_code == 400

    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])

# Reset Password - Invalid Password
def test_reset_password_invalid_password():
    # Create a test user
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create reset token for test user
    token = create_action_token(ActionTokenType.reset, user_id)

    # Reset password with invalid password
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "weak"})
    assert r.status_code == 422

    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])

# Reset Password - Wrong ActionToken Type (verify token used)
def test_reset_password_wrong_type():
    # Create a test user
    r = client.post("/users/", json={"name": "User", "email": "reset@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Create verify token
    token = create_action_token(ActionTokenType.verify, user_id)

    # Reset password with verify token
    r = client.post(f"/auth/reset-password/{token.id}", json={"password": "NewPassword123!"})
    assert r.status_code == 400

    # Clean up test data
    client.delete(f"/users/{user_id}")
    save_all([t for t in load_all() if t.get("id") != token.id])

# Reset Password - Not Found
def test_reset_password_na():
    r = client.post("/auth/reset-password/00000000-0000-0000-0000-000000000000", json={"password": "NewPassword123!"})
    assert r.status_code == 404