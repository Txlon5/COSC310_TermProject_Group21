from fastapi.testclient import TestClient
from app.main import app
from app.routers.orders import orders_store, notification, unauthorized_access_log

client = TestClient(app)

def setup_function():
    orders_store.clear()        #Clear orders from in-memory store before each test 
    notification.clear_notifications()      #Clear notifications before each test
    unauthorized_access_log.clear()     #Clear recorded unauthorized access attempts
    
def test_get_certain_past_order_not_found_when_order_does_not_exist():
    response = client.get("/orders/history/user123/nonexistent-order-id", headers = {"X-User-Id": "user123"})       #Attempt to retrieve an order that does not exist in memory store
    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found."}     #Returns 404 when order not found.
    
def test_get_certain_past_orders_show_unauthorized_when_order_belongs_to_another_user():
    order_request = {"user_id": "user123", "restaurant_id": "restaurantB", "items": ["Mandi"]}
    
    create_response = client.post("/orders", json = order_request)
    assert create_response.status_code == 201
    
    order_id = create_response.json()["order_id"]       #Fetches the generated order id
    response = client.get(f"/orders/history/user999/{order_id}", headers = {"X-User-Id": "user999"})        #Attempt to retrieve an order belonging to a different user
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to view this order."}

def test_get_certain_past_order_displays_full_order_details():
    #sample order
    order_request = {"user_id": "user456", "restaurant_id": "restaurantA", "items": ["Shawarma", "Fries"]}
    create_response = client.post("/orders", json = order_request)
    assert create_response.status_code == 201
    
    created_order = create_response.json()
    order_id = created_order["order_id"]        #Extracts the generated order id from created order
    response = client.get(f"/orders/history/user456/{order_id}", headers = {"X-User-Id": "user456"})        #Request selected past order using the user and order id
    assert response.status_code == 200
    
    data = response.json()      #Parse
    
    #Verifies the order returned matches the one created before with correct timestamps
    assert data["order_id"] == order_id
    assert data["user_id"] == "user456"
    assert data["restaurant_id"] == "restaurantA"
    assert data["items"] == ["Shawarma", "Fries"]
    assert data["status"] == "Created"
    assert "created_at" in data
    assert "updated_at" in data
    assert data["delivered_at"] is None
    
def test_get_certain_past_order_reflects_updated_status():
    order_request = {"user_id": "user789", "restaurant_id": "restaurantC", "items":["Butter Chicken"]}
    
    create_response = client.post("/orders", json=order_request)
    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    update_response = client.patch(f"/orders/{order_id}/status",json={"status": "Preparing"})       # Update the order status to Preparing
    assert update_response.status_code == 200
    
    response = client.get(f"/orders/history/user789/{order_id}", headers = {"X-User-Id": "user789"})
    assert response.status_code == 200

    data = response.json()

    # Confirming that the returned order reflects the updated status
    assert data["order_id"] == order_id
    assert data["user_id"] == "user789"
    assert data["restaurant_id"] == "restaurantC"
    assert data["items"] == ["Butter Chicken"]
    assert data["status"] == "Preparing"
    assert data["delivered_at"] is None         # Since the order is not delivered yet, it should still be None
