from fastapi.testclient import TestClient
from app.main import app
from app.schemas.card_validator import CardValidator
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
        role="admin"
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

# Card Number Validation
def test_card_num_validation():
    assert CardValidator.is_valid_card_num("1234567890123")         # True - 13 digits
    assert CardValidator.is_valid_card_num("1234567890123456")      # True - 16 digits
    assert CardValidator.is_valid_card_num("1234567890123456789")   # True - 19 digits
    assert not CardValidator.is_valid_card_num("123456789012")      # False - 12 digits (too short)
    assert not CardValidator.is_valid_card_num("12345678901234567890") # False - 20 digits (too long)
    assert not CardValidator.is_valid_card_num("123456789012a")     # False - contains letter
    assert not CardValidator.is_valid_card_num("1234-5678-9012")    # False - contains special characters
    assert not CardValidator.is_valid_card_num("")                  # False - blank entry

# CVC Validation
def test_cvc_validation():
    assert CardValidator.is_valid_cvc("123")                        # True - 3 digits
    assert CardValidator.is_valid_cvc("1234")                       # True - 4 digits
    assert not CardValidator.is_valid_cvc("12")                     # False - 2 digits (too short)
    assert not CardValidator.is_valid_cvc("12345")                  # False - 5 digits (too short)
    assert not CardValidator.is_valid_cvc("12a")                    # False - contains letter
    assert not CardValidator.is_valid_cvc("")                       # False - blank entry

# Expiry Validation
def test_expiry_validation():
    assert CardValidator.is_valid_expiry("2026-03")                 # True
    assert CardValidator.is_valid_expiry("2024-12")                 # True
    assert not CardValidator.is_valid_expiry("26-03")               # False - wrong year format
    assert not CardValidator.is_valid_expiry("2026/03")             # False - wrong separator
    assert not CardValidator.is_valid_expiry("2026-13")             # False - month > 12
    assert not CardValidator.is_valid_expiry("2026-00")             # False - month < 01
    assert not CardValidator.is_valid_expiry("abcd-ef")             # False - contains letter
    assert not CardValidator.is_valid_expiry("")                    # False - blank entry

# Name Validation
def test_name_validation():
    assert CardValidator.is_valid_name("John Smith")                # True
    assert CardValidator.is_valid_name("Mary Ann")                  # True
    assert not CardValidator.is_valid_name("John123")               # False - contains numbers
    assert not CardValidator.is_valid_name("John Smith!")           # False - special character
    assert not CardValidator.is_valid_name("John_Smith")            # False - special character
    assert not CardValidator.is_valid_name("")                      # False - blank entry

# Address Validation
def test_address_validation():
    assert CardValidator.is_valid_address("123 Main St")            # True
    assert CardValidator.is_valid_address("556 Sarsons Rd, Kelowna, BC") # True
    assert CardValidator.is_valid_address("Apt-4B 123 Main")        # True
    assert not CardValidator.is_valid_address("123 Main St!")       # False - invalid special character
    assert not CardValidator.is_valid_address("123 Main #4")        # False - invalid special character
    assert not CardValidator.is_valid_address("")                   # False - blank entry


# Integration Tests

# Card Retrival by ID - Valid
def test_get_card():
    # Create test card
    r = client.post(
        "/payments/cards/",
        json={
            "card_num": "4868719196829038",
            "card_cvc": "344",
            "card_exp": "2029-11",
            "holder_name": "John Smith",
            "holder_address": "556 Sarsons Rd, V1W5H5, Kelowna, BC"
        }
    )
    # Check card was created successfully
    assert r.status_code == 201

    # Retrieve test card_id
    card_id = r.json()["id"]

    r = client.get(f"/payments/cards/{card_id}")
    assert r.status_code == 200
    assert r.json() == {
        "id": card_id,
        "user_id": "8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",        
        "card_num": "************9038",
        "card_cvc": "***",
        "card_exp": "2029-11",
        "holder_name": "John Smith",
        "holder_address": "556 Sarsons Rd, V1W5H5, Kelowna, BC"
    }
    # Clean up test data
    r = client.delete(f"/payments/cards/{card_id}")

# Card Retrival by ID - Not Found
def test_get_card_na():
    r = client.get("/payments/cards/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404

# Card Create - Valid
def test_create_user():
    # Create test card
    r = client.post(
        "/payments/cards/",
        json={
            "card_num": "4868719196829038",
            "card_cvc": "344",
            "card_exp": "2029-11",
            "holder_name": "John Smith",
            "holder_address": "556 Sarsons Rd, V1W5H5, Kelowna, BC"
        }
    )
    
    # Check card was created successfully
    assert r.status_code == 201

    # Save json response to variable
    data = r.json() 
    
    # Check if id exists and is not empty
    assert "id" in data
    assert data["id"] != ""

    # Check that returned card data matches input
    assert data["card_num"] == "4868719196829038"
    assert data["card_cvc"] == "344"
    assert data["card_exp"] == "2029-11"
    assert data["holder_name"] == "John Smith"
    assert data["holder_address"] == "556 Sarsons Rd, V1W5H5, Kelowna, BC"

    # Clean up test data
    r = client.delete(f"/payments/cards/{data['id']}")


# Card Delete - Valid
def test_delete_user():
    # Create test card
    r = client.post(
        "/payments/cards/",
        json={
            "card_num": "4868719196829038",
            "card_cvc": "344",
            "card_exp": "2029-11",
            "holder_name": "John Smith",
            "holder_address": "556 Sarsons Rd, V1W5H5, Kelowna, BC"
        }
    )
    # Check card was created successfully
    assert r.status_code == 201

    # Delete card
    card_id = r.json()["id"]
    r = client.delete(f"/payments/cards/{card_id}")
    
    # Check card was deleted successfully
    assert r.status_code == 204