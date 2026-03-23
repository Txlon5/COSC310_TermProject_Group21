from app.services.notification_service import NotificationService
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
notification = NotificationService()

def setup_function():
    notification.clear_notifications()      #Clear notifications before each test 
    #orders_store.clear()                    #Clear orders from in-memory store before each test
    
def test_status_change_for_missing_orders_generates_404():
    response = client.patch("/orders/nonexistent-orderid/status",
    json = {"status": "Preparing"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found."}
    
def test_same_status_generates_400():
    order_request = {"user_id" : "user123", "restaurant_id" : 1, "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Pizza"}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    order_id = create_response.json()["order_id"]
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Created"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Order status remains unchanged."}
    
    user_notifications = notification.get_notifications_for_user("user123")
    assert len(user_notifications) == 1     #Ensures that no new notification was updated when trying to update to the same status. Only the original order created notification should exist.
    assert user_notifications[0].type == "Order_Created"
    
def test_order_status_change_generates_notification():
    order_request = {"user_id" : "user333", "restaurant_id" : 3, "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Biriyani"}, {"menuItemId": 2, "quantity": 1, "item_name": "Lassi"}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    created_order = create_response.json()
    order_id = created_order["order_id"]
    update_response = client.patch(f"/orders/{order_id}/status", json={"status": "Preparing"})
    assert update_response.status_code == 200
    updated_order = update_response.json()
    assert updated_order["status"] == "Preparing"
    
    user_notifications = notification.get_notifications_for_user("user333")
    assert len(user_notifications) == 2     #Now, two notifications exist, one for order created and one for order status changed.
    
    status_notification = user_notifications[1]     #The second notification for the status change. Th efirst stays intact for the order created event.
    assert status_notification.user_id == "user333"
    assert status_notification.order_id == order_id
    assert status_notification.type == "Order_Status_Changed"
    assert status_notification.title == "Order Status Updated"
    assert status_notification.message == (f"Your order {order_id} status has been changed from Created to Preparing.")
    assert status_notification.timestamp is not None
    
def test_status_change_creates_only_one_notification():
    order_request = {"user_id" : "user999", "restaurant_id" : 999, "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Sushi"}]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201
    
    order_id = create_response.json()["order_id"]
    
    response_1 = client.patch(f"/orders/{order_id}/status", json={"status": "Preparing"})
    assert response_1.status_code == 200
    user_notifications = notification.get_notifications_for_user("user999")
    assert len(user_notifications) == 2     #Two notifications should exist, one for order created and one for the status change.
    assert user_notifications[0].type == "Order_Created"
    assert user_notifications[1].type == "Order_Status_Changed"
    
    response_2 = client.patch(f"/orders/{order_id}/status", json={"status": "Ready"})
    assert response_2.status_code == 200
    user_notifications = notification.get_notifications_for_user("user999")
    assert len(user_notifications) == 3     #Now three notifications should exist, one for order created and two for the two status changes.
    assert user_notifications[2].type == "Order_Status_Changed"    
    assert user_notifications[2].message == (f"Your order {order_id} status has been changed from Preparing to Ready.")