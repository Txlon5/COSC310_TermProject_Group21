from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.user_validator import UserValidator
from app.auth.password_utils import PasswordHandler
from app.auth.token_utils import get_current_user
from app.schemas.user import User
client = TestClient(app)

# Create mock user for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="User",
        email="user@example.com",
        password="password123!",
        role="user"
    )

# Overide get_current_user() function to return the mock user
@pytest.fixture(autouse=True)
def apply_admin_override():
    # Set the override
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Pause to allow test to run with override
    yield 
    # Clear the override after test is done
    app.dependency_overrides = {}

# Integration Tests

# User Retrive All Users - Invalid Authorization
def test_get_users():
    r = client.get("/users/")
    assert r.status_code == 403

# User Retrival by ID - Invalid Authorization
def test_get_user():
    r = client.get("/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7")
    assert r.status_code == 403

# # User Retrival by Email - Invalid Authorization
def test_get_user_email():
    r = client.get("/users/email/jane.doe@example.com")
    assert r.status_code == 403

# User Delete - Invalid Authorization
def test_delete_user():
    r = client.delete(f"/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7")
    assert r.status_code == 403

# User Update - Invalid Authorization
def test_update_user():
    r = client.put("/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", json={"name": "User", "email": "updateme@example.com", "password": "Password123!"})
    assert r.status_code == 403