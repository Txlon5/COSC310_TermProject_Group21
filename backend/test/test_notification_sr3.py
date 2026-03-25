from fastapi.testclient import TestClient
from app.services.notification_service import NotificationService
from app.main import app
from unittest.mock import patch, MagicMock
import pytest

client = TestClient(app)
notification = NotificationService()

RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

def setup_function():
    notification.clear_notifications()     #Clear notifications before each test 

# Test Setup - Setup Mock data/function calls for MenuItem Checks and Fetching/Saving Orders
@pytest.fixture(autouse=True)
def setup_test_environment():
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
    
    # Clear overrides after test is done
    app.dependency_overrides = {}
        
def test_get_notifications_for_user_with_no_notifications_returns_empty_list():
    #checks that when no notifications exist for a user, an empty list is returned.
    response = client.get("/notifications/userabc")
    assert response.status_code == 200  #request must succeed if no notification exists for the user, but it should return an empty list.
    assert response.json() == []
    
def test_get_notifications_for_user_returns_all_notifications():
    #Checks that notificaions created during order creation and status change are correctly retrieved for a user.
    order_request = {
        "user_id": "user456",
        "card_id": "test-card-id",
        "restaurant_id": RESTAURANT_ID,
        "delivery_method": "delivery",
        "items": [
            {"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 1},
            
        ]
    }

    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    # Update the status so a second notification is generated.
    update_response = client.patch(f"/orders/{order_id}/status", json={"status": "preparing"})
    assert update_response.status_code == 200
    
    #retrieve notifications for the user and check that both the order created and order status changed notifications are returned.
    response = client.get("/notifications/user456")
    assert response.status_code == 200
    
    #now we convert JSOn response to a list of notifications and check their contents.
    #we are expecting two notifications, one for order created and one for order status changed.
    data = response.json()
    assert len(data) == 2
    
    #Check the contents of the first notification for order created event and the second notification for order status changed event.
    assert data[0]["user_id"] == "user456"
    assert data[0]["order_id"] == order_id
    assert data[0]["type"] == "Order_Created"
    assert data[0]["title"] == "Order Created"
    assert data[0]["message"] == (f"Your order {order_id} has been created successfully.")
    assert "timestamp" in data[0]
    assert data[0]["timestamp"] is not None
    
    assert data[1]["user_id"] == "user456"
    assert data[1]["order_id"] == order_id
    assert data[1]["type"] == "Order_Status_Changed"
    assert data[1]["title"] == "Order Status Updated"
    assert data[1]["message"] == (f"Your order {order_id} status has been changed from created to preparing.")
    assert "timestamp" in data[1]
    assert data[1]["timestamp"] is not None
    

def test_get_notifications_returns_requested_users_notifications_only():
    #Checks that when retrieving notifications for a specific user, only that user's notifications are returned and not notifications for other users.
    order_request1 = {"user_id" : "user1",
        "card_id": "test-card-id",
        "restaurant_id" : RESTAURANT_ID,
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 1}]
    }
    order_request2 = {
        "user_id" : "user2",
        "card_id": "test-card-id",
        "restaurant_id" : RESTAURANT_ID,
        "delivery_method": "delivery",
        "items": [{"menuItemId": 1, "name": "Cheesey Bread", "price": 15.0, "quantity": 1}]
    }
    
    create_response1 = client.post("/orders", json=order_request1)
    create_response2 = client.post("/orders", json=order_request2)
    assert create_response1.status_code == 201
    assert create_response2.status_code == 201
    
    order_id1 = create_response1.json()["order_id"]
    order_id2 = create_response2.json()["order_id"]
    
    #Now we retrieve notifications for user1 and check that only user1's notification is returned, not user2's notification.
    response = client.get("/notifications/user1")
    assert response.status_code == 200
    
    #Only one notification should be returned for user1, which is the order created notification for their order.
    data = response.json()
    assert len(data) == 1     
    assert data[0]["user_id"] == "user1"
    assert data[0]["order_id"] == order_id1
    assert data[0]["type"] == "Order_Created"
    assert data[0]["title"] == "Order Created"
    assert data[0]["message"] == (f"Your order {order_id1} has been created successfully.")
    assert "timestamp" in data[0]
    assert data[0]["timestamp"] is not None

    
