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
        id="userabc",
        name="User",
        email="user@example.com",
        password="password123!",
        role="user"
    )

# Create mock user for mismatch testing
def override_get_current_user_mismatch():
    return User(
        id="user999",
        name="Other User",
        email="other@example.com",
        password="password123!",
        role="user"
    )

# Test Setup - Setup Mock data/function calls for MenuItem Checks and Fetching/Saving Orders
@pytest.fixture(autouse=True)
def setup_test_environment():
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

    # Clear the auth override after the test
    app.dependency_overrides = {}

def test_get_order_history_requires_authentication():
    order_request = {"user_id": "user123", "card_id": "test-card-id", "restaurant_id": "restaurantA", "items": [{"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 10.0}], "delivery_method": "delivery", }
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201

    #No authentication header provided
    response = client.get("/orders/history/user123")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    
def test_get_selected_order_rejects_wrong_authenticated_user():
    create_response = client.post("/orders", json={
        "user_id": "user456", 
        "card_id": "test-card-id",
        "restaurant_id": "restaurantB", 
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 10.0}]
    })
    assert create_response.status_code == 201
    

    #Wrong authenticated user tries to access a certain order
    app.dependency_overrides[get_current_user] = override_get_current_user_mismatch
    response = client.get("/orders/history/user456")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to perform this action."}
    
    
def test_get_order_history_allows_authenticated_user_to_view_own_orders():
    # Create two orders for user123 and one for a different user to verify mismatch
    response_1 = client.post("/orders", json={
        "user_id": "userabc", 
        "card_id": "test-card-id",
        "restaurant_id": "restaurant1", 
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 10.0}]
    })
    response_2 = client.post("/orders", json={
        "user_id": "userabc", 
        "card_id": "test-card-id",
        "restaurant_id": "restaurant2", 
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "quantity": 2, "name": "Fries", "price": 5.0}]
    })
    response_3 = client.post("/orders", json={
        "user_id": "user999", 
        "card_id": "test-card-id",
        "restaurant_id": "restaurantC", 
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Pasta", "price": 15.0}]
    })

    assert response_1.status_code == 201
    assert response_2.status_code == 201
    assert response_3.status_code == 201

    app.dependency_overrides[get_current_user] = override_get_current_user
    response = client.get("/orders/history/userabc")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    # Check for recent order
    assert data[0]["user_id"] == "userabc"
    assert all(order["user_id"] == "userabc" for order in data)
    
def test_get_order_history_rejects_access_to_another_users_orders():
    create_response = client.post("/orders", json={
        "user_id": "user123", 
        "card_id": "test-card-id",
        "restaurant_id": "restaurantA", 
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Sushi", "price": 20.0}]
    })
    assert create_response.status_code == 201

    #When user999 tries to access user123's order history
    app.dependency_overrides[get_current_user] = override_get_current_user_mismatch
    response = client.get("/orders/history/user123")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to perform this action."}
