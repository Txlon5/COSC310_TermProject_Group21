from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_subtotal_single_item():
    payload = {
        "restaurant_id": "1",
        "items": [
            {
                "item_id": "1",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["subtotal"] == 8.99
    assert data["tax"] == 1.08
    assert data["delivery_fee"] == 0.0
    assert data["total"] == 10.07


def test_subtotal_multiple_items():
    payload = {
        "restaurant_id": "1",
        "items": [
            {"item_id": "1", "quantity": 2},
            {"item_id": "2", "quantity": 1}
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["subtotal"] == 21.97
    assert data["tax"] == 2.64
    assert data["delivery_fee"] == 0.0
    assert data["total"] == 24.61


def test_subtotal_quantity_change():
    payload = {
        "restaurant_id": "1",
        "items": [
            {"item_id": "2", "quantity": 3}
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["subtotal"] == 11.97
    assert data["tax"] == 1.44
    assert data["delivery_fee"] == 0.0
    assert data["total"] == 13.41