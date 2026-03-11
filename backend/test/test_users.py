from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user_validator import UserValidator
from app.auth.password_utils import PasswordHandler
from app.services.users_service import login_user
client = TestClient(app)

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
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea"}

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
    assert r.json() == {"id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7", "name": "Jane Doe", "email": "jane.doe@example.com", "password": "a109e36947ad56de1dca1cc49f0ef8ac9ad9a7b1aa0df41fb3c4cb73c1ff01ea"}

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

# Get Hash Password
def test_get_password_hash_via_email():
    assert login_user("jane.doe@example.com","Password123!")