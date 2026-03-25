import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

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


def test_update_delivered_order_api():
    # Create a delivery order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": RESTAURANT_ID,
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
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2,"name": "Soda", "price": 6.0, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]
    

def test_update_picked_up_order_api():
    # Create a pickup order
    response = client.post("/orders", json={
        "user_id": "testuser",
        "restaurant_id": RESTAURANT_ID,
        "items": [{"menuItemId": 2,"name": "Soda", "price": 6.0, "quantity": 1}],
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    })
    assert response.status_code == 201
    order_id = response.json()["order_id"]

    # Move through valid status transitions for pickup
    assert client.patch(f"/orders/{order_id}/status", json={"status": "preparing"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "ready"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "pickedup"}).status_code == 200
    
    # Try to update the completed (picked up) order
    response = client.put(f"/orders/{order_id}", json=[{"menuItemId": 2,"name": "Cheesey Bread", "price": 15.0, "quantity": 2}])
    assert response.status_code == 400
    assert "completed" in response.json()["detail"]