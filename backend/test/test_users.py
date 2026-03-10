from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Unit Tests
from app.schemas.user_validator import UserValidator

# Email Validation
def test_email_validation():
    assert UserValidator.is_valid_email("user@example.com")         # True
    assert not UserValidator.is_valid_email("!user@example.com")    # False - special character in name
    assert not UserValidator.is_valid_email("user@examp!le.com")    # False - special character in website
    assert not UserValidator.is_valid_email("user@example.co!m")    # False - special character in .com
    assert not UserValidator.is_valid_email("userexample.com")      # False - no @ symbol
    assert not UserValidator.is_valid_email("user@example")         # False - no .com
    assert not UserValidator.is_valid_email("@example.com")         # False - no username
    assert not UserValidator.is_valid_email("")                     # False - blank entry

# Password Validation
def test_password_validation():
    assert UserValidator.is_valid_password("Password1!")            # True
    assert not UserValidator.is_valid_password("Pass1!")            # False - too short
    assert not UserValidator.is_valid_password("password1!")        # False - no capitals
    assert not UserValidator.is_valid_password("Password1")         # False - no special character
    assert not UserValidator.is_valid_password("")                  # False - blank entry


# Integration Tests

# User Retrival
def test_get_user():
    r = client.get("/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7")
    assert r.status_code == 200
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "test"}

def test_get_user_na():
    r = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404

# User Creation
def test_create_user():
    r = client.post(
        "/users/",
        json={"name": "User", "email": "user@example.com", "password": "Password123!"},
    )
    assert r.status_code == 201

    # Save json response to variable
    data = r.json() 

    # Check if id exists and is not empty
    assert "id" in data
    assert data["id"] != ""

    # Check that returned user data matches input
    assert data["name"] == "User"
    assert data["email"] == "user@example.com"
    assert data["password"] == "Password123!"

# User Creation - Email Conflict
def test_create_user_conflict():
    r = client.post(
        "/users/",
        json={"name": "Talon Lusk", "email": "txlon5@student.ubc.ca", "password": "Password123!"},
    )
    assert r.status_code == 409

def test_create_user_invalid_email():
    r = client.post(
        "/users/",
        json={"name": "User", "email": "example", "password": "Password123!"},
    )
    assert r.status_code == 422

def test_create_user_invalid_password():
    r = client.post(
        "/users/",
        json={"name": "User", "email": "user@example.com", "password": "pass"},
    )
    assert r.status_code == 422

# User Deletion
def test_delete_user():
    r = client.post("/users/", json={"name": "User", "email": "user@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]
    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 204

def test_delete_user_na():
    r = client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


