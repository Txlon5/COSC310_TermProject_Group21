from fastapi.testclient import TestClient
from app.main import app
from app.schemas.menu import MenuItem
import app.routers.order_cost as order_cost_router


client = TestClient(app)

RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"





def test_subtotal_single_item():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "1",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 26.0
    }


def test_subtotal_multiple_items():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "1",
                "quantity": 2
            },
            {
                "item_id": "2",
                "quantity": 1
            }
        ]
    }

    # Burger 8.99 x 2 = 17.98
    # Fries  3.99 x 1 = 3.99
    # subtotal = 21.97

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 67.0
    }


def test_subtotal_quantity_change():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "2",
                "quantity": 3
            }
        ]
    }

    # Fries 3.99 x 3 = 11.97
    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "subtotal": 45.0
    }


def test_subtotal_invalid_menu_item():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "999",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_subtotal_missing_restaurant():
    payload = {
        "restaurant_id": "doese-not-exist",
        "items": [
            {
                "item_id": "1",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 404

def test_subtotal_invalid_quantity():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "1",
                "quantity": 0
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 422
