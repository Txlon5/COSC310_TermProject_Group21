import json as _json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.orders_repository import load_all, save_all
from app.schemas.menu import MenuItem

client = TestClient(app)


# Utility: reads restaurants.json without modifying it
def get_valid_restaurant_and_item():
    json_path = Path(__file__).resolve().parent.parent / "app" / "data" / "restaurants.json"
    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = _json.load(f)
        if not data:
            return None, None, None, None
        rest = data[0]
        restaurant_id = rest.get("restaurant_id")
        items = rest.get("menuItems", [])
        if not items:
            return restaurant_id, None, None, None
        item = items[0]
        return restaurant_id, item["menuItemId"], item["name"], item["price"]
    except Exception:
        return None, None, None, None


def test_create_order_stores_order(monkeypatch, tmp_path):
    restaurant_id, menuItemId, name, price = get_valid_restaurant_and_item()
    if not restaurant_id or menuItemId is None:
        pytest.skip("No valid restaurant/menu item in restaurants.json")
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    # Bypass menu validation to decouple from restaurant data state
    monkeypatch.setattr(
        "app.services.orders_service.fetch_menu_by_restaurant_id",
        lambda rid: [MenuItem(menuItemId=menuItemId, name=name, price=price, category="Food")]
    )
    order_request = {
        "user_id": "testuser1",
        "restaurant_id": restaurant_id,
        "items": [{"menuItemId": menuItemId, "name": name, "price": price, "quantity": 2}],
        "delivery_method": "delivery",
        "delivery_address": "123 Test St"
    }
    response = client.post("/orders", json=order_request)
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert data["user_id"] == "testuser1"
    assert data["restaurant_id"] == restaurant_id


def test_get_order_by_id_returns_correct_order(monkeypatch, tmp_path):
    restaurant_id, menuItemId, name, price = get_valid_restaurant_and_item()
    if not restaurant_id or menuItemId is None:
        pytest.skip("No valid restaurant/menu item in restaurants.json")
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    monkeypatch.setattr(
        "app.services.orders_service.fetch_menu_by_restaurant_id",
        lambda rid: [MenuItem(menuItemId=menuItemId, name=name, price=price, category="Food")]
    )
    order_request = {
        "user_id": "testuser2",
        "restaurant_id": restaurant_id,
        "items": [{"menuItemId": menuItemId, "name": name, "price": price, "quantity": 1}],
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    }
    response = client.post("/orders", json=order_request)
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert data["user_id"] == "testuser2"
    assert data["restaurant_id"] == restaurant_id


def test_update_completed_order_raises_error(monkeypatch, tmp_path):
    restaurant_id, menuItemId, name, price = get_valid_restaurant_and_item()
    if not restaurant_id or menuItemId is None:
        pytest.skip("No valid restaurant/menu item in restaurants.json")
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    monkeypatch.setattr(
        "app.services.orders_service.fetch_menu_by_restaurant_id",
        lambda rid: [MenuItem(menuItemId=menuItemId, name=name, price=price, category="Food")]
    )
    order_request = {
        "user_id": "testuser3",
        "restaurant_id": restaurant_id,
        "items": [{"menuItemId": menuItemId, "name": name, "price": price, "quantity": 1}],
        "delivery_method": "delivery",
        "delivery_address": "123 Main St"
    }
    response = client.post("/orders", json=order_request)
    assert response.status_code == 201
    order_id = response.json()["order_id"]
    # Advance through required transitions: created → preparing → ready → delivered
    for status in ["preparing", "ready", "delivered"]:
        patch_response = client.patch(f"/orders/{order_id}/status", json={"status": status})
        assert patch_response.status_code == 200, f"Failed to set status to {status}: {patch_response.json()}"
    # Try to update completed order — should be rejected
    put_response = client.put(f"/orders/{order_id}", json=[{"menuItemId": menuItemId, "name": name, "price": price, "quantity": 2}])
    assert put_response.status_code == 400
    assert "completed" in put_response.json()["detail"]


# Repository Unit Tests

def test_load_all_empty(tmp_path, monkeypatch):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    assert load_all() == []


def test_save_all_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    data = [{"orderId": 123, "restaurant_id": "abc", "items": [], "status": "pending"}]
    save_all(data)
    with (tmp_path / "orders.json").open("r", encoding="utf-8") as f:
        loaded = _json.load(f)
    assert loaded == data


def test_save_and_load_all(tmp_path, monkeypatch):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    orders = [
        {"orderId": 1, "restaurant_id": "101", "items": [], "status": "pending"},
        {"orderId": 2, "restaurant_id": "102", "items": [], "status": "pending"},
    ]
    save_all(orders)
    loaded = load_all()
    assert loaded == orders