from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_assign_delivery_info_to_existing_order():
    create_response = client.post("/orders", json={
        "user_id": "u1",
        "restaurant_id": "r1",
        "items": ["Pizza"]
    })
    assert create_response.status_code == 201

    order_id = create_response.json()["order_id"]

    update_response = client.put(f"/orders/{order_id}/delivery", json={
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        
    })
    print(update_response.json())
    assert update_response.status_code == 200

    body = update_response.json()
    assert body["delivery_method"] == "delivery"
    assert body["delivery_address"] == "123 Test St"