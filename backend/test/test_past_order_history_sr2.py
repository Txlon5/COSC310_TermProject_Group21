from app.services.notification_service import NotificationService
from fastapi.testclient import TestClient
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.main import app
from unittest.mock import patch, MagicMock
import pytest

client = TestClient(app)
notification = NotificationService()

def setup_function():
    notification.clear_notifications()      #Clear notifications before each test  

# Create mock user for testing
def override_get_current_user():
    return User(
        id="4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7",
        name="User",
        email="user@example.com",
        password="password123!",
        role="user"
    )

# Create mock admin for testing
def override_get_current_user_admin():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29300f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )

# Test Setup - Setup Mock data/function calls for MenuItem Checks and Fetching/Saving Orders
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Set the auth override
    app.dependency_overrides[get_current_user] = override_get_current_user_admin
    # Mock Order Database
    fake_db = []
    # Mock MenuItems
    mock_menu_item1 = MagicMock()
    mock_menu_item1.menuItemId = 1
    mock_menu_item2 = MagicMock()
    mock_menu_item2.menuItemId = 2
    
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
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item1, mock_menu_item2]):
        yield

    # Clear the auth override after the test
    app.dependency_overrides = {}

def test_get_certain_past_order_not_found_when_order_does_not_exist():
    response = client.get("/orders/history/4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7")
    assert response.status_code == 200
    assert response.json() == []
    
def test_get_certain_past_orders_show_unauthorized_when_order_belongs_to_another_user():
    #sample order
    order_request = {
        "user_id": "user123",
        "card_id": "test-card-id",
        "restaurant_id": "24",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Nuggets", "price": 6.99}
        ]
    }

    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    # Switch to user account to test unauthorized access
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # Check that we are not allowed to access orders from user123
    response = client.get(f"/orders/history/user123")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to perform this action."}

    # Switch back to admin account
    app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_certain_past_order_displays_full_order_details():
    #sample order
    order_request = {
        "user_id": "4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7",
        "card_id": "test-card-id",
        "restaurant_id": "28",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 8.99},
            {"menuItemId": 2, "quantity": 1, "name": "Fries", "price": 3.99}
        ]
    }

    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    created_order = create_response.json()
    order_id = created_order["order_id"]

    response = client.get(f"/orders/history/4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7")
    assert response.status_code == 200
    
    result = response.json()
    data = result[0] if isinstance(result, list) else result
    
    #Verifies the order returned matches the one created before with correct timestamps
    assert data["order_id"] == order_id
    assert data["user_id"] == "4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7"
    assert str(data["restaurant_id"]) == "28"
    assert data["items"] == [
        {"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 8.99}, 
        {"menuItemId": 2, "quantity": 1, "name": "Fries", "price": 3.99}
    ]
    assert data["status"] == "created"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["delivered_at"] is None
    
def test_get_certain_past_order_reflects_updated_status():
    order_request = {
        "user_id": "4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7",
        "card_id": "test-card-id",
        "restaurant_id": "12",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Butter Chicken", "price": 14.99}
        ]
    }
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    update_response = client.patch(f"/orders/{order_id}/status", json={"status": "preparing"})
    assert update_response.status_code == 200
    
    response = client.get(f"/orders/history/4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7")
    assert response.status_code == 200
    
    result = response.json()
    data = result[0] if isinstance(result, list) else result

    # Confirming that the returned order reflects the updated status
    assert data["order_id"] == order_id
    assert data["user_id"] == "4c6dbfcb-72c5-4cc4-9f76-29300f0ecda7"
    assert str(data["restaurant_id"]) == "12"
    assert data["items"] == [{"menuItemId": 1, "quantity": 1, "name": "Butter Chicken", "price": 14.99}]
    assert data["status"] == "preparing"
    assert data["delivered_at"] is None         # Since the order is not delivered yet, it should still be None
