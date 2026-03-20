from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_order_by_id():
    # Create an order using valid CSV data
    create_response = client.post("/orders", json={
        "user_id": "bf8fe126-f8ce-4299-b347-30dcf6b36ff7",  # customer_id from CSV
        "restaurant_id": 21,  # restaurant_id from CSV
        "items": [
            {"menuItemId": 1, "quantity": 2, "item_name": "Taccos"}  # food_item from CSV
        ],
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        "pickup_location": ""
    })
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    # Retrieve the order by ID
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    order = get_response.json()
    assert order["order_id"] == order_id
    assert order["user_id"] == "bf8fe126-f8ce-4299-b347-30dcf6b36ff7"
    assert order["restaurant_id"] == 21
    assert order["delivery_method"] == "delivery"
    assert order["delivery_address"] == "123 Test St"
    assert order["items"][0]["item_name"] == "Taccos"
