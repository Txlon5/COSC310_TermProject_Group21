from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_order_not_found():
    response = client.get("/orders/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_update_order_status_not_found():
    response = client.put(
        "/orders/9999/status",
        json={"new_status": "preparing"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_update_order_status_invalid():
    response = client.put(
        "/orders/1/status",
        json={"new_status": "bad_status"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status"
    
def test_get_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_order_by_id():
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_update_order_status_success():
    response = client.put(
        "/orders/1/status",
        json={"new_status": "preparing"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Order status updated successfully"
    assert data["order"]["status"] == "preparing"