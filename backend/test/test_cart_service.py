import pytest
from app.services import cart_service
from app.repositories import cart_repository
from datetime import datetime

@pytest.fixture(autouse=True)
def isolated_cart(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.cart_repository.DATA_PATH", tmp_path / "cart.json")
    cart_repository.save_all([])

def test_save_and_get_cart():
    user_id = "user_minimal"
    cart = {
        "user_id": user_id,
        "restaurant_id": "85590c53-fc55-4837-a3ef-283345df572a",
        "items": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    cart_service.save_cart(cart)
    loaded = cart_service.get_cart_by_user_id(user_id)
    assert loaded is not None
    assert loaded["user_id"] == user_id

def test_update_cart():
    user_id = "user_minimal"
    cart = {
        "user_id": user_id,
        "restaurant_id": "85590c53-fc55-4837-a3ef-283345df572a",
        "items": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    cart_service.save_cart(cart)
    cart["items"].append({"menuItemId": 1, "name": "Burger", "price": 5.0, "quantity": 2})
    cart_service.save_cart(cart)
    loaded = cart_service.get_cart_by_user_id(user_id)
    assert len(loaded["items"]) == 1
    assert loaded["items"][0]["name"] == "Burger"

def test_delete_cart():
    user_id = "user123"
    cart = {
        "user_id": user_id,
        "restaurant_id": "rest1",
        "items": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    cart_service.save_cart(cart)
    cart_service.delete_cart_by_user_id(user_id)
    loaded = cart_service.get_cart_by_user_id(user_id)
    assert loaded is None

def test_get_cart_nonexistent():
    assert cart_service.get_cart_by_user_id("no_such_user") is None

def test_delete_cart():
    user_id = "user123"
    cart = {
        "user_id": user_id,
        "restaurant_id": "rest1",
        "items": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    cart_service.save_cart(cart)
    cart_service.delete_cart_by_user_id(user_id)
    loaded = cart_service.get_cart_by_user_id(user_id)
    assert loaded is None

def test_get_cart_nonexistent():
    assert cart_service.get_cart_by_user_id("no_such_user") is None

def test_cart_subtotal():
    user_id = "user_subtotal"
    cart = {
        "user_id": user_id,
        "restaurant_id": "85590c53-fc55-4837-a3ef-283345df572a",
        "items": [
            {"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 2},
            {"menuItemId": 2, "name": "Cheesey Bread", "price": 15.0, "quantity": 1}
        ],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    cart_service.save_cart(cart)
    loaded = cart_service.get_cart_by_user_id(user_id)
    assert loaded is not None
    assert "subtotal" in loaded
    # Subtotal should be = (2 * 26.0) + (1 * 15.0) = 67.0
    assert loaded["subtotal"] == 67.0