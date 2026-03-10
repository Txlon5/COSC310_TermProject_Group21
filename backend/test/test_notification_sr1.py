from backend.app.main import app
from backend.app.routers.orders import notification
from fastapi.testclient import TestClient

client = TestClient(app)

def setup_function():
    notification.clear_notifications()     #Clear notifications before each test 
    
def test_create_order_notification():
    order_request = {
        "user_id": "user123",
        "restaurant_id": "restaurant123",
        "items": ["Pizza", "Soda"]
    }
    
    response = client.post("/orders", json=order_request)
    assert response.status_code == 201
    data = response.json()
    created_order_id = data["order_id"]
    user_notifications = notification.get_notifications_for_user("user123")     #fetch notification for specific user from the in-memory store.
    assert len(user_notifications) == 1     #Assert that one notification was created for the user.
    
    notif = user_notifications[0]
    #validate notif contents
    assert notif.user_id == "user123"
    assert notif.order_id == created_order_id
    assert notif.type == "Order_Created"
    assert notif.title == "Order Created"
    assert notif.message == f"Your order {created_order_id} has been created successfully."
    
def test_notification_associated_with_correct_user():
    order_request = {
        "user_id": "Adam22",
        "restaurant_id": "restaurant456",
        "items": ["Burger"]
    }
    client.post("/orders", json=order_request)
    adam22_notifications = notification.get_notifications_for_user("Adam22")
    bob99_notifications = notification.get_notifications_for_user("Bob99")
    
    assert len(adam22_notifications) == 1     #Assert that Adam22 has one notification.
    assert len(bob99_notifications) == 0     #Assert that Bob99 has no notifications.
    
def test_each_created_order_generates_its_own_notification():
    #two notifs should be generated for two different orders
    order_request1 = {
        "user_id": "Charlie33",
        "restaurant_id": "restaurant789",
        "items": ["Pasta"]
    }
    order_request2 = {
        "user_id": "Charlie33",
        "restaurant_id": "restaurant456",
        "items": ["Salad"]
    }
    
    response_1 = client.post("/orders", json=order_request1)
    response_2 = client.post("/orders", json=order_request2)
    
    assert response_1.status_code == 201
    assert response_2.status_code == 201
    
    charlie_notifications = notification.get_notifications_for_user("Charlie33")
    assert len(charlie_notifications) == 2     #Assert that Charlie33 has two notifications for the two orders created.
    
    order_ids = {response_1.json()["order_id"], response_2.json()["order_id"]}
    notif_order_ids = {n.order_id for n in charlie_notifications}
    
    assert order_ids == notif_order_ids     #Assert that the notifications are associated with the correct order IDs.

def test_invalid_order_request_does_not_generate_notification():
    #If order creation fails, no notification should be generated. This tests the validation of the order creation endpoint and ensures that notifications are only created for valid orders.
    invalid_order_request = {
        "user_id": "Dave44",
        "restaurant_id": "restaurant123",
        "items": []
    }
    
    response = client.post("/orders", json=invalid_order_request)
    assert response.status_code == 422     #Assert that the request is invalid due to missing items field.
    
    dave_notifications = notification.get_notifications_for_user("Dave44")
    assert len(dave_notifications) == 0     #Assert that no notification was generated for the invalid order request.
    
    
    
    
    
        