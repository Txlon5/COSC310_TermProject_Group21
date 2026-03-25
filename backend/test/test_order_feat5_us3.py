import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.orders_repository import save_all

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

@pytest.fixture(autouse=True)
def isolated_orders(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    save_all([])

def test_assign_delivery_info_to_existing_order():
     # First create an order that we can later update with delivery information
    create_response = client.post("/orders", json={
        "user_id": "u1",
        "card_id": "test-card-id",
        "restaurant_id": RESTAURANT_ID,
        "items": [{"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 1}]
    })
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    update_response = client.put(f"/orders/{order_id}/delivery", json={
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        
    })
   
    assert update_response.status_code == 200

    body = update_response.json()
    assert body["delivery_method"] == "delivery"
    assert body["delivery_address"] == "123 Test St"
