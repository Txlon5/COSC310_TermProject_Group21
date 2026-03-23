import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.orders_repository import save_all

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"


def setup_function():
    # Clear orders before each API test.
    save_all([])

def test_update_delivered_order_api():
    # Create a delivery order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": 19,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "delivery",
        "delivery_address": "123 Main St"
    })
    assert response.status_code == 201
    order_id = response.json()["order_id"]

   

    # Move it into a completed state.
    assert client.patch(f"/orders/{order_id}/status", json={"status": "preparing"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "ready"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "delivered"}).status_code == 200


    # Try to update the completed order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2,"name": "Cheesey Bread", "price": 15.0, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]
    
def test_update_picked_up_order_api():
    # Create a pickup order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": 19,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    })
    assert response.status_code == 201
    order_id = response.json()["order_id"]

    # Move through valid status transitions for pickup
    assert client.patch(f"/orders/{order_id}/status", json={"status": "Preparing"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "Ready"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "Picked up"}).status_code == 200
    

    # Try to update the completed (picked up) order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2,"name": "Cheesey Bread", "price": 15.0, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]