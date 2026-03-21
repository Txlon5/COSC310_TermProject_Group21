import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_update_delivered_order_api():
    # Create an order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": 19,
        "items": [{"menuItemId": 1, "quantity": 1}],
        "delivery_method": "delivery",
        "delivery_address": "123 Main St"
    })
    assert response.status_code == 201
    order_id = response.json()["order_id"]

    # Mark order as ready via API

    response = client.patch(f"/orders/{order_id}/status", json={"status": "Preparing"})
    assert response.status_code == 200
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Ready"})
    assert response.status_code == 200
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Delivered"})
    assert response.status_code == 200

    # Try to update the completed order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]
    
def test_update_picked_up_order_api():
    # Create a pickup order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": 19,
        "items": [{"menuItemId": 1, "quantity": 1}],
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    })
    assert response.status_code == 201
    order_id = response.json()["order_id"]

    # Move through valid status transitions for pickup
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Preparing"})
    assert response.status_code == 200
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Ready"})
    assert response.status_code == 200
    response = client.patch(f"/orders/{order_id}/status", json={"status": "Picked up"})
    assert response.status_code == 200

    # Try to update the completed (picked up) order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]