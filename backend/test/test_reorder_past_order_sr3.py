import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.schemas.payment_method import CreditCard
from app.schemas.payment_transaction import PaymentStatusType
from app.services.notification_service import NotificationService

client = TestClient(app)
notification = NotificationService()


def setup_function():
    notification.clear_notifications()    # Clear notifications before each test


# Mock authenticated owner user
def override_get_current_user_owner():
    return User(
        id="user123",
        name="Owner User",
        email="owner@example.com",
        password="password123!",
        role="user"
    )


@pytest.fixture(autouse=True)
def setup_test_environment():
    app.dependency_overrides[get_current_user] = override_get_current_user_owner

    fake_db = []

    mock_menu_item1 = MagicMock()
    mock_menu_item1.menuItemId = 1

    mock_menu_item2 = MagicMock()
    mock_menu_item2.menuItemId = 2

    fake_card = CreditCard(
        id="card-123",
        user_id="user123",
        card_num="4111111111111111",
        card_cvc="123",
        card_exp="2030-12",
        holder_name="Owner User",
        holder_address="123 Main St"
    )

    def mock_load():
        return fake_db.copy()

    def mock_save(data):
        fake_db.clear()
        fake_db.extend(data)

    with patch("app.services.orders_service.load_all", side_effect=mock_load), \
         patch("app.services.orders_service.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item1, mock_menu_item2]), \
         patch("app.services.orders_service.get_card_for_user", return_value=fake_card), \
         patch("app.services.orders_service.create_transaction", return_value=PaymentStatusType.pending):
        yield fake_db

    app.dependency_overrides = {}


# Ensures a user can reorder a past delivery order and override it to pickup.
def test_reorder_past_order_overrides_delivery_method_to_pickup(setup_test_environment):
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantA",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Burger", "price": 10.0}
        ]
    })
    assert response.status_code == 201

    original_order = response.json()
    original_order_id = original_order["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123",
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    })
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    assert reordered_order["order_id"] != original_order_id
    assert reordered_order["delivery_method"] == "pickup"
    assert reordered_order["pickup_location"] == "Front Desk"
    assert reordered_order["delivery_address"] is None


# Ensures a user can reorder a past pickup order and override it to delivery.
def test_reorder_past_order_overrides_delivery_method_to_delivery(setup_test_environment):
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantB",
        "delivery_method": "pickup",
        "pickup_location": "Store Counter",
        "items": [
            {"menuItemId": 2, "quantity": 2, "name": "Pizza", "price": 15.0}
        ]
    })
    assert response.status_code == 201

    original_order = response.json()
    original_order_id = original_order["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123",
        "delivery_method": "delivery",
        "delivery_address": "456 UBC Ave"
    })
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    assert reordered_order["order_id"] != original_order_id
    assert reordered_order["delivery_method"] == "delivery"
    assert reordered_order["delivery_address"] == "456 UBC Ave"
    assert reordered_order["pickup_location"] is None


# Ensures the original order's delivery method is reused when none is provided in the reorder request.
def test_reorder_past_order_uses_original_delivery_method_when_not_overridden(setup_test_environment):
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantC",
        "delivery_method": "delivery",
        "delivery_address": "789 Pine Rd",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Wrap", "price": 12.0}
        ]
    })
    assert response.status_code == 201

    original_order = response.json()
    original_order_id = original_order["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123"
    })
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    assert reordered_order["order_id"] != original_order_id
    assert reordered_order["delivery_method"] == "delivery"
    assert reordered_order["delivery_address"] == "789 Pine Rd"
    assert reordered_order["pickup_location"] is None


# Ensures reorder fails if delivery is selected but no delivery address is available.
def test_reorder_past_order_requires_delivery_address_for_delivery(setup_test_environment):
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantD",
        "delivery_method": "pickup",
        "pickup_location": "Pickup Spot",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Nuggets", "price": 8.0}
        ]
    })
    assert response.status_code == 201

    original_order_id = response.json()["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123",
        "delivery_method": "delivery"
    })
    assert reorder_response.status_code == 400
    assert reorder_response.json() == {
        "detail": "delivery_address is required when delivery_method is 'delivery'."
    }


# Ensures reorder fails if pickup is selected but no pickup location is available.
def test_reorder_past_order_requires_pickup_location_for_pickup(setup_test_environment):
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantE",
        "delivery_method": "delivery",
        "delivery_address": "999 River St",
        "items": [
            {"menuItemId": 2, "quantity": 1, "name": "Pasta", "price": 13.0}
        ]
    })
    assert response.status_code == 201

    original_order_id = response.json()["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123",
        "delivery_method": "pickup"
    })
    assert reorder_response.status_code == 400
    assert reorder_response.json() == {"detail": "pickup_location is required when delivery_method is 'pickup'."}


# Ensures overriding the delivery method does not modify the original stored order.
def test_reorder_past_order_does_not_modify_original_delivery_fields(setup_test_environment):
    fake_db = setup_test_environment

    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantF",
        "delivery_method": "delivery",
        "delivery_address": "111 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Burger", "price": 10.0}
        ]
    })
    assert response.status_code == 201

    original_order = response.json()
    original_order_id = original_order["order_id"]

    original_snapshot = fake_db[0].copy()

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={
        "card_id": "card-123",
        "delivery_method": "pickup",
        "pickup_location": "Front Desk"
    })
    assert reorder_response.status_code == 201

    # Original order remains unchanged
    assert fake_db[0] == original_snapshot
    assert fake_db[0]["delivery_method"] == "delivery"
    assert fake_db[0]["delivery_address"] == "111 Main St"
    assert fake_db[0]["pickup_location"] is None

    # New reordered order uses overridden fields
    assert fake_db[1]["delivery_method"] == "pickup"
    assert fake_db[1]["pickup_location"] == "Front Desk"
    assert fake_db[1]["delivery_address"] is None