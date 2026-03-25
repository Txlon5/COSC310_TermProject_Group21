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

# Create mock admin for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )

# Test Setup - Setup Mock data/function calls for MenuItem Checks and Fetching/Saving Orders
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Set the auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
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


def test_get_past_order_history_for_user_returns_empty_list():
    #verifies that APi returns empty list instead of an error when the user has no past order in history.
    response = client.get("/orders/history/no_orders_user")
    assert response.status_code == 200
    assert response.json() == []        #Returned order history is an empty list
    
def test_get_past_order_history_returns_orders_for_that_user_only():
    #Verifies that order history belonging to a specific user is returned.
    order_1 = {"user_id": "user123",
        "restaurant_id": "24",
        "delivery_method": "delivery",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Nuggets", "price": 6.99}
        ]
    }
    response_1 = client.post("/orders", json = order_1)
    assert response_1.status_code == 201
    
    order_2 = {
        "user_id": "user123", 
        "restaurant_id": "14", 
        "delivery_method": "delivery",
        "items": [
            {"menuItemId": 2, "quantity": 1, "name": "Burger", "price": 10.99}
        ]
    }
    
    response_2 = client.post("/orders", json = order_2)
    assert response_2.status_code == 201
    
    order_3 = {"user_id": "user888",
        "restaurant_id": "34",
        "delivery_method": "delivery",
        "items": [
            {"menuItemId": 2, "quantity": 1, "name": "Burger", "price": 10.99},
            {"menuItemId": 1, "quantity": 1, "name": "Nuggets", "price": 6.99}
        ]
    }
    response_3 = client.post("/orders", json = order_3)
    assert response_3.status_code == 201
    
    created_order_id_1 = response_1.json()["order_id"]      #extracts generated order IDs to later verify that correct orders were returned
    created_order_id_2 = response_2.json()["order_id"]
    created_order_id_3 = response_3.json()["order_id"]
    
    history_response = client.get("/orders/history/user123")        #Retrieves order history for user123 and later converts to python data
    assert history_response.status_code == 200
    data = history_response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2       #validates only two orders belong to user123
    
    returned_ids = {order["order_id"] for order in data}        
    assert returned_ids == {created_order_id_1, created_order_id_2}     #verifies orders returned matches user123 created orders
    assert created_order_id_3 not in returned_ids       #verifies another user order is not included.
    
    returned_restaurants = {order["restaurant_id"] for order in data}
    assert returned_restaurants == {"24", "14"}       #verifies correct restaurants are associated
    
    for order in data:
        assert order["user_id"] == "user123"
        assert "order_id" in order
        assert "restaurant_id" in order
        assert "items" in order
        assert "status" in order
        assert "created_at" in order
        assert "updated_at" in order
        assert "delivered_at" in order
        assert order["status"] == "created"
        assert order["delivered_at"] is None