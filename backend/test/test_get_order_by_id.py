import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.user import User

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

# Create mock admin for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )

@pytest.fixture(autouse=True)
def setup_test_environment():
    # Set user auth to mock user
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Mock Order Database
    fake_db = []
    
    # Mock MenuItems
    mock_menu_item = MagicMock()
    mock_menu_item.menuItemId = 1

    # Return mock list
    def mock_load():
        return fake_db.copy() 
    
    # Save mock list
    def mock_save(data):
        fake_db.clear()
        fake_db.extend(data)
    
    # Apply mock functions
    with patch("app.services.orders_service.load_all", side_effect=mock_load), \
         patch("app.services.orders_service.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item]):
        yield
        
    # Clear mock overrides after test is done
    app.dependency_overrides.clear()


def test_get_order_by_id():
    # Create an order using valid CSV data
    create_response = client.post("/orders", json={
        "user_id": "8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",  # customer_id from mock user
        "restaurant_id": RESTAURANT_ID,                     # restaurant_id from mock data
        "items": [
            {"menuItemId": 1, "quantity": 2, "name": "Taccos", "price": 12.99} # food_item from list
        ],
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        "pickup_location": ""
    })
    
    # Check order was created
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    # Retrieve the order by ID
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    order = get_response.json()
    
    # Validate order
    assert order["order_id"] == order_id
    assert order["user_id"] == "8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7"
    assert order["restaurant_id"] == RESTAURANT_ID
    assert order["delivery_method"] == "delivery"
    assert order["delivery_address"] == "123 Test St"
    assert order["items"][0]["name"] == "Taccos"