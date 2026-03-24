from fastapi.testclient import TestClient
from app.main import app
from app.repositories.orders_repository import save_all

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

def test_invalid_delivery_method():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id":RESTAURANT_ID ,
        "items": [{"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "drone"
    })
    assert response.status_code == 422


def test_delivery_without_address_is_currently_accepted():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": RESTAURANT_ID,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "delivery"
    })
    assert response.status_code == 201


def test_pickup_without_location_is_not_accepted():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "pickup"
    })
    assert response.status_code == 422


def test_delivered_status_sets_timestamp():
    create = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id":  RESTAURANT_ID,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}]
    })

    order_id = create.json()["order_id"]

    assert client.patch(f"/orders/{order_id}/status", json={"status": "preparing"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "ready"}).status_code == 200
    response3 = client.patch(f"/orders/{order_id}/status", json={"status": "delivered"})
    assert response3.status_code == 200
    assert response3.json()["delivered_at"] is not None