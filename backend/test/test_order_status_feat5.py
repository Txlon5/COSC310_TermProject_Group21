from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_delivery_method():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Pizza"}],
        "delivery_method": "drone"
    })
    assert response.status_code == 400


def test_delivery_requires_address():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Pizza"}],
        "delivery_method": "delivery"
    })
    assert response.status_code == 400


def test_pickup_requires_location():
    response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Pizza"}],
        "delivery_method": "pickup"
    })
    assert response.status_code == 400


def test_delivered_status_sets_timestamp():
    create = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1, "quantity": 1, "item_name": "Pizza"}]
    })

    order_id = create.json()["order_id"]

    response1 = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "Preparing"}
    )
    assert response1.status_code == 200

    response2 = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "Ready"}
    )
    assert response2.status_code == 200

    response3 = client.patch(
        f"/orders/{order_id}/status",
        json={"status": "Delivered"}
    )
    assert response3.status_code == 200
    assert response3.json()["delivered_at"] is not None