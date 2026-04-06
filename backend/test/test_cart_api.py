import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories import cart_repository, orders_repository

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_cart(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.cart_repository.DATA_PATH", tmp_path / "cart.json")
    cart_repository.save_all([])

@pytest.fixture(autouse=True)
def prevent_order_writes(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    orders_repository.save_all([])

RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"
USER_ID = "testuser"
CARD_ID = "testcard"


def test_add_item_to_cart():
    resp = client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 2
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == USER_ID
    assert data["restaurant_id"] == RESTAURANT_ID
    assert data["items"][0]["menuItemId"] == 1
    assert data["items"][0]["quantity"] == 2


def test_get_cart():
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 2,
        "quantity": 1
    })
    resp = client.get(f"/cart/get?user_id={USER_ID}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == USER_ID
    assert data["items"][0]["menuItemId"] == 2


def test_checkout_cart():
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 3,
        "quantity": 1
    })
    resp = client.post("/cart/checkout", json={
        "user_id": USER_ID,
        "card_id": CARD_ID,
        "delivery_method": "delivery",
        "delivery_address": "123 Main St"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == USER_ID
    assert data["restaurant_id"] == RESTAURANT_ID
    assert data["items"][0]["menuItemId"] == 3
    # Cart should be cleared after checkout
    cart_resp = client.get(f"/cart/get?user_id={USER_ID}")
    assert cart_resp.json() is None


def test_add_after_checkout():
    # Checkout first
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 1
    })
    client.post("/cart/checkout", json={
        "user_id": USER_ID,
        "card_id": CARD_ID,
        "delivery_method": "delivery",
        "delivery_address": "123 Main St"
    })
    # Then we can add again
    resp = client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 2,
        "quantity": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"][0]["menuItemId"] == 2
    assert data["items"][0]["quantity"] == 1


def test_add_invalid_menu_item():
    resp = client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 999,
        "quantity": 1
    })
    assert resp.status_code == 400
    assert "Invalid menuItemId" in resp.text


def test_checkout_invalid_delivery_method():
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 1
    })
    resp = client.post("/cart/checkout", json={
        "user_id": USER_ID,
        "card_id": CARD_ID,
        "delivery_method": "not_a_valid_method",
        "delivery_address": "123 Main St"
    })
    assert resp.status_code == 400
    assert "delivery_method" in resp.text


def test_update_item_quantity():
    # Add an item
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 2
    })
    # Then update its quantity
    resp = client.post("/cart/update-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 5
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"][0]["quantity"] == 5


def test_remove_item_from_cart():
    # Add an item
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 2
    })
    # Remove item (ie set quantity to 0)
    resp = client.post("/cart/update-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert all(item["menuItemId"] != 1 for item in data["items"])


def test_update_item_quantity_to_zero_removes_item():
    # Try adding two items
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 2
    })
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 2,
        "quantity": 1
    })
    # Remove first item by setting quantity to 0
    resp = client.post("/cart/update-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 1,
        "quantity": 0
    })
    assert resp.status_code == 200
    data = resp.json()
    assert all(item["menuItemId"] != 1 for item in data["items"])
    assert any(item["menuItemId"] == 2 for item in data["items"])


def test_update_item_quantity_reflected_in_cart():
    # Add item
    client.post("/cart/add-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 3,
        "quantity": 1
    })
    # Update quantity
    resp = client.post("/cart/update-item", json={
        "user_id": USER_ID,
        "restaurant_id": RESTAURANT_ID,
        "menu_item_id": 3,
        "quantity": 4
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"][0]["quantity"] == 4
    # Get cart and check again
    resp2 = client.get(f"/cart/get?user_id={USER_ID}")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["items"][0]["quantity"] == 4