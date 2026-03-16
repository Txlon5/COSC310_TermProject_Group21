from fastapi.testclient import TestClient
from app.routers.orders import orders_store, notification, unauthorized_access_log
from app.main import app

client = TestClient(app)

def setup_function():
    orders_store.clear()        #Clear orders from in-memory store before each test
    notification.clear_notifications()      #Clear notifications before each test
    unauthorized_access_log.clear()     #Clear recorded unauthorized access attempts
    
def test_get_order_history_requires_authentication():
    order_request = {"user_id": "user123", "restaurant_id": "restaurantA", "items": ["Burger"]}
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201

    #No authentication header provided, confirm unauthorized attempt was recorded in the log
    response = client.get("/orders/history/user123")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required."}
    assert len(unauthorized_access_log) == 1
    assert unauthorized_access_log[0]["requested_user_id"] == "user123"
    assert unauthorized_access_log[0]["authenticated_user_id"] is None
    
def test_get_selected_order_rejects_wrong_authenticated_user():
    create_response = client.post("/orders", json={"user_id": "user456", "restaurant_id": "restaurantB", "items": ["Shawarma"]})
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]
    

    #Wrong authenticated user tries to access a certain order
    response = client.get(f"/orders/history/user456/{order_id}", headers={"X-User-Id": "user999"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to access this order history."}
    assert len(unauthorized_access_log) == 1
    assert unauthorized_access_log[0]["requested_user_id"] == "user456"
    assert unauthorized_access_log[0]["authenticated_user_id"] == "user999"
    
def test_get_order_history_allows_authenticated_user_to_view_own_orders():
    # Create two orders for user123 and one for a different user to verify mismatch
    response_1 = client.post("/orders", json={"user_id": "userabc", "restaurant_id": "restaurant1", "items": ["Pizza"]})
    response_2 = client.post("/orders", json={"user_id": "userabc", "restaurant_id": "restaurant2", "items": ["Fries"]})
    response_3 = client.post("/orders", json={"user_id": "user999", "restaurant_id": "restaurantC", "items": ["Pasta"]})
    
    assert response_1.status_code == 201
    assert response_2.status_code == 201
    assert response_3.status_code == 201

    response = client.get("/orders/history/userabc", headers={"X-User-Id": "userabc"})

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert all(order["user_id"] == "userabc" for order in data)
    
def test_get_order_history_rejects_access_to_another_users_orders():
    create_response = client.post("/orders", json={"user_id": "user123", "restaurant_id": "restaurantA", "items": ["Sushi"]})
    assert create_response.status_code == 201

    #When user999 tries to access user123's order history
    response = client.get("/orders/history/user123", headers={"X-User-Id": "user999"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to access this order history."}

    #Confirm unauthorized attempt was recorded in the log
    assert len(unauthorized_access_log) == 1
    assert unauthorized_access_log[0]["requested_user_id"] == "user123"
    assert unauthorized_access_log[0]["authenticated_user_id"] == "user999"