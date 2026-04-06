from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user_validator import UserValidator
from app.auth.password_utils import PasswordHandler
from app.auth.token_utils import get_current_user
from app.schemas.user import User
import pytest
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
        is_verified=True
    )

# Overide get_current_user() function to return the mock admin
@pytest.fixture(autouse=True)
def apply_admin_override():
    # Set the override
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Pause to allow test to run with override
    yield 
    # Clear the override after test is done
    app.dependency_overrides = {}

# Unit Tests

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
    assert not UserValidator.is_valid_password("Passw1!")           # False - 7 characters
    assert UserValidator.is_valid_password("Passwo1!")              # True  - 8 characters

# Role Validation
def test_role_validation():
    assert UserValidator.is_valid_role("user")                      # True
    assert UserValidator.is_valid_role("admin")                     # True
    assert not UserValidator.is_valid_role("moderator")             # False - invalid role
    assert not UserValidator.is_valid_role("")                      # False - blank entry
    
# Password Hash
def test_hash_password():
    hashed = PasswordHandler.hash_password("Password123!")
    assert hashed != "Password123!"                                 # True - Check password is not plain text
    assert PasswordHandler.hash_password("Password123!") == hashed    # True - Manually hashed password matches

# Integration Tests

# User Retrival by ID - Valid
def test_get_user():
    r = client.get("/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7")
    assert r.status_code == 200
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea", "role": "user", "is_verified": True}

# User ID Retrival by ID - Not Found
def test_get_user_na():
    r = client.get("/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404

# User Retrival by ID - All Users
def test_get_users():
    r = client.get("/users/")
    assert r.status_code == 200
    assert len(r.json()) > 0                                        # Check that list of users is not empty

# User Retrival by Email - Valid
def test_get_user_email():
    r = client.get("/users/email/jane.doe@example.com")
    assert r.status_code == 200
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea", "role": "user", "is_verified": True}

# User Retrival by Email- Not Found
def test_get_user_by_email_na():
    r = client.get("/users/email/jane@example.com")
    assert r.status_code == 404

# User Create - Valid
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
    assert data["password"] == PasswordHandler.hash_password("Password123!")  # Check is hashed

    # Clean up test data
    client.delete(f"/users/{data['id']}")

# User Create - Email Conflict
def test_create_user_conflict():
    r = client.post(
        "/users/",
        json={"name": "Jane Doe", "email": "jane.doe@example.com", "password": "Password123!"},
    )
    assert r.status_code == 409

# User Create - Invalid Email
def test_create_user_invalid_email():
    r = client.post(
        "/users/",
        json={"name": "User", "email": "example", "password": "Password123!"},
    )
    assert r.status_code == 422

# User Create - Invalid Password
def test_create_user_invalid_password():
    r = client.post(
        "/users/",
        json={"name": "User", "email": "user@example.com", "password": "pass"},
    )
    assert r.status_code == 422

# User Delete - Valid
def test_delete_user():
    r = client.post("/users/", json={"name": "User", "email": "user@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]
    r = client.delete(f"/users/{user_id}")
    assert r.status_code == 204

# User Delete - Not Found
def test_delete_user_na():
    r = client.delete("/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404

# User Update - Valid
def test_update_user():
    r = client.post("/users/", json={"name": "User", "email": "updateme@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    r = client.put(
        f"/users/{user_id}",
        json={"name": "Updated User", "email": "updated@example.com", "password": "NewPassword123!"},
    )
    assert r.status_code == 200

    # Save json response to variable
    data = r.json()

    # Check if id exists and is not empty
    assert "id" in data
    assert data["id"] != ""

    # Check that returned user data matches input
    assert data["name"] == "Updated User"
    assert data["email"] == "updated@example.com"
    assert data["password"] == PasswordHandler.hash_password("NewPassword123!")  # Check is hashed

    # Clean up test data
    client.delete(f"/users/{data['id']}")

# User Update - Not Found
def test_update_user_na():
    r = client.put(
        "/users/00000000-0000-0000-0000-000000000000",
        json={"name": "User", "email": "user@example.com", "password": "Password123!"},
    )
    assert r.status_code == 404

# User Update - Email Conflict
def test_update_user_email_conflict():
    # Create test user
    r = client.post("/users/", json={"name": "User", "email": "user@example.com", "password": "Password123!"})
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Update email
    r = client.put(
        f"/users/{user_id}",
        json={"name": "User", "email": "jane.doe@example.com", "password": "Password123!"},
    )
    assert r.status_code == 409

    # Clean up test data
    client.delete(f"/users/{user_id}")

# User Update - Invalid Email
def test_update_user_invalid_email():
    r = client.put(
        "/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        json={"name": "Jane Doe", "email": "user", "password": "Password123!"},
    )
    assert r.status_code == 422

# User Update - Invalid Password
def test_update_user_invalid_password():
    r = client.put(
        "/users/9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        json={"name": "Jane Doe", "email": "jane.doe@example.com", "password": "pass"},
    )
    assert r.status_code == 422


# Current User Routes

# User Retrieval Self - Valid
def test_get_self():
    r = client.get("/users/self")
    assert r.status_code == 200
    assert r.json() == {"id": "8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7", "name": "Admin", "email":"admin@example.com", "password":"password123!", "role":"admin", "is_verified": True}

# User Update Self - Valid
def test_update_self():
    # Create user to update
    r = client.post(
        "/users/",
        json={"name": "Updated User", "email": "updateme@example.com", "password": "Password123!"}
    )
    assert r.status_code == 201
    
    # Swap current_user to be the new test user 
    def override_get_current_user():
        return User(**r.json()) # Load r as current user
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Perform self update
    r = client.put(
        "/users/self",
        json={"name": "User Updated", "email": "updated@example.com", "password": "NewPassword123!"}
    )
    data = r.json()

    # Check if id exists and is not empty
    assert "id" in data
    assert data["id"] != ""

    # Check that returned user data matches input
    assert data["name"] == "User Updated"
    assert data["email"] == "updated@example.com"
    assert data["password"] == PasswordHandler.hash_password("NewPassword123!")  # Check is hashed

    # Set override back to admin so we can delete test user
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Clean up test data
    client.delete(f"/users/{data['id']}")

# User Delete Self - Valid
def test_delete_self():
    # Create user to delete
    r = client.post(
        "/users/",
        json={"name": "User", "email": "user@example.com", "password": "Password123!"}
    )
    assert r.status_code == 201
    user_id = r.json()["id"]

    # Swap current_user to be the new test user 
    def override_test_user():
        return User(**r.json()) # Load r as current user
    app.dependency_overrides[get_current_user] = override_test_user

    # Self delete
    r = client.delete("/users/self")
    assert r.status_code == 204

    # Set override back to admin
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Verify user is deleted
    r = client.get(f"/users/{user_id}")
    assert r.status_code == 404

   

    
