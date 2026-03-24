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


# Integration Tests

# Card Retrival by ID - Valid
def test_get_card():
    r = client.get("/payments/cards/83abbe8d-00fa-4a30-94e9-61ca5016022f")
    assert r.status_code == 200
    assert r.json() == {
        "id": "83abbe8d-00fa-4a30-94e9-61ca5016022f",
        "user_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        "card_num": "string",
        "card_cvc": "string",
        "card_exp": "string",
        "holder_name": "string",
        "holder_address": "string"
    }

# Card Retrival by ID - Not Found
def test_get_card_na():
    r = client.get("/payments/cards/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404

# Card Create - Valid
def test_create_user():
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