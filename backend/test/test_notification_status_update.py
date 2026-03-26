from app.services.notification_service import NotificationService
from app.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest

client = TestClient(app)
notification = NotificationService()

def setup_function():
    notification.clear_notifications()      #Clear notifications before each test 

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

def test_status_change_for_missing_orders_generates_404():
    response = client.patch("/orders/nonexistent-orderid/status",
    json = {"status": "preparing"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found."}
    
def test_same_status_generates_400():
    order_request = {"user_id" : "user123", "card_id": "test-card-id", "restaurant_id" : "6fc1000b-6494-4f0e-b8a1-4888f669f975", "delivery_method": "delivery", "items": [{"menuItemId": 1, "quantity": 1, "name": "Pizza", "price": 12.99}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    order_id = create_response.json()["order_id"]
    response = client.patch(f"/orders/{order_id}/status", json={"status": "created"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Order status remains unchanged."}
    
    user_notifications = notification.get_notifications_for_user("user123")
    assert len(user_notifications) == 1     #Ensures that no new notification was updated when trying to update to the same status. Only the original order created notification should exist.
    assert user_notifications[0].type == "Order_Created"
    
def test_order_status_change_generates_notification():
    order_request = {"user_id" : "user333", "card_id": "test-card-id", "restaurant_id" : "6fc1000b-6494-4f0e-b8a1-4888f669f975", "delivery_method": "delivery", "items": [{"menuItemId": 1, "quantity": 1, "name": "Biriyani", "price": 15.00}, {"menuItemId": 1, "quantity": 1, "name": "Lassi", "price": 5.00}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    created_order = create_response.json()
    order_id = created_order["order_id"]
    update_response = client.patch(f"/orders/{order_id}/status", json={"status": "preparing"})
    assert update_response.status_code == 200
    updated_order = update_response.json()
    assert updated_order["status"] == "preparing"
    
    user_notifications = notification.get_notifications_for_user("user333")
    assert len(user_notifications) == 2     #Now, two notifications exist, one for order created and one for order status changed.
    
    status_notification = user_notifications[1]     #The second notification for the status change. Th efirst stays intact for the order created event.
    assert status_notification.user_id == "user333"
    assert status_notification.order_id == order_id
    assert status_notification.type == "Order_Status_Changed"
    assert status_notification.title == "Order Status Updated"
    assert status_notification.message == (f"Your order {order_id} status has been changed from created to preparing.")
    assert status_notification.timestamp is not None
    
def test_status_change_creates_only_one_notification():
    order_request = {"user_id" : "user999", "card_id": "test-card-id", "restaurant_id" : "6fc1000b-6494-4f0e-b8a1-4888f669f975", "delivery_method": "delivery", "items": [{"menuItemId": 1, "quantity": 1, "name": "Sushi", "price": 22.00}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    order_id = create_response.json()["order_id"]
    
    response_1 = client.patch(f"/orders/{order_id}/status", json={"status": "preparing"})
    assert response_1.status_code == 200
    user_notifications = notification.get_notifications_for_user("user999")
    assert len(user_notifications) == 2     #Two notifications should exist, one for order created and one for the status change.
    assert user_notifications[0].type == "Order_Created"
    assert user_notifications[1].type == "Order_Status_Changed"
    
    response_2 = client.patch(f"/orders/{order_id}/status", json={"status": "ready"})
    assert response_2.status_code == 200
    user_notifications = notification.get_notifications_for_user("user999")
    assert len(user_notifications) == 3     #Now three notifications should exist, one for order created and two for the two status changes.
    assert user_notifications[2].type == "Order_Status_Changed"    
    assert user_notifications[2].message == (f"Your order {order_id} status has been changed from preparing to ready.")
