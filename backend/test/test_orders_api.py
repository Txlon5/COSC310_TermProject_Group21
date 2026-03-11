"""
Feat 4 - Sr2
This file exists to test the API stuff without needing to start the server
For as much as I've tested it, this is a sanity check
"""


import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_update_completed_order_api():
    # Create an order
    response = client.post("/orders", json={
        "restaurantId": 19,
        "items": [{"menuItemId": 1, "quantity": 1}]
    })
    assert response.status_code == 200
    order_id = response.json()["orderId"]

    # Mark order as completed via API
    response = client.patch(f"/orders/{order_id}/status", json="completed")
    assert response.status_code == 200

    # Try to update the completed order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]