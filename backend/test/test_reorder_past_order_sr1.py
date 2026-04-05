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
    notification.clear_notifications()      # Clear notifications before each test

# Mock authenticated user for testing - Owner of the order
def override_get_current_user_owner():
    return User(
        id="user123",
        name="Owner User",
        email="owner@example.com",
        password="password123!",
        role="user"
    )

# Mock authenticated user for testing - different user (not owner of the order)
def override_get_current_user_other_user():
    return User(
        id="user999",
        name="Other User",
        email="other@example.com",
        password="password123!",
        role="user"
    )

#test setup with mock mem, menu items, mock payment and card validation.
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
        
    # Applying patches to the orders service functions that interact with external dependencies/data storage
    with patch("app.services.orders_service.load_all", side_effect=mock_load), \
         patch("app.services.orders_service.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item1, mock_menu_item2]), \
         patch("app.services.orders_service.get_card_for_user", return_value=fake_card), \
         patch("app.services.orders_service.create_transaction", return_value=PaymentStatusType.pending):
        yield fake_db

    # Clean up after tests
    app.dependency_overrides = {}

#Ensures reorder creates a brand new order with same data.
def test_reorder_past_order_creates_new_order_from_original_order(setup_test_environment):
    fake_db = setup_test_environment

    #create original order to reorder from
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantA",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 2, "name": "Burger", "price": 10.0},
            {"menuItemId": 2, "quantity": 1, "name": "Fries", "price": 5.0}
        ]
    }

    create_response = client.post("/orders", json=original_order_request)
    assert create_response.status_code == 201

    original_order = create_response.json()
    original_order_id = original_order["order_id"]

    # Reorder the original order
    reorder_request = {
        "card_id": "card-123"
    }

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json=reorder_request)
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    # Validating new order creation
    assert reordered_order["order_id"] != original_order["order_id"]        #generates new order id
    assert reordered_order["user_id"] == "user123"
    assert reordered_order["restaurant_id"] == original_order["restaurant_id"]
    assert reordered_order["items"] == original_order["items"]
    assert reordered_order["status"] == "created"
    assert reordered_order["delivery_method"] == original_order["delivery_method"]
    assert reordered_order["delivery_address"] == original_order["delivery_address"]
    assert reordered_order["pickup_location"] == original_order["pickup_location"]
    assert reordered_order["delivered_at"] is None

    # Ensure original order is unchanged in the fake_db and that the new order is added.
    assert len(fake_db) == 2

# Ensures original order data remains unchanged after reorder attempt.
def test_reorder_past_order_does_not_modify_original_order(setup_test_environment):
    fake_db = setup_test_environment

    # Create original order
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantB",
        "delivery_method": "delivery",
        "delivery_address": "456 Oak Ave",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Pizza", "price": 15.0}]
    })
    assert response.status_code == 201

    original_order = response.json()
    original_order_id = original_order["order_id"]

    # Save snapshot of original order
    original_snapshot = fake_db[0].copy()

    # Reorder
    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json={"card_id": "card-123"})
    assert reorder_response.status_code == 201
    
    assert fake_db[0] == original_snapshot  # Ensure original order unchanged
    assert fake_db[1]["order_id"] != fake_db[0]["order_id"] # Ensure new order exists separately

#Ensure user cannot reorder another user's order, enforcing security check.
def test_reorder_past_order_rejects_another_users_order(setup_test_environment):
    # Create order as user123
    response = client.post("/orders", json={
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantC",
        "delivery_method": "delivery",
        "delivery_address": "789 Pine Rd",
        "items": [{"menuItemId": 1, "quantity": 1, "name": "Shawarma", "price": 12.0}]
    })
    assert response.status_code == 201

    order_id = response.json()["order_id"]

    # Switch to different user
    app.dependency_overrides[get_current_user] = override_get_current_user_other_user

    # Attempt reorder
    response = client.post(f"/orders/reorder/{order_id}", json={"card_id": "card-123"})

    # Expect unauthorized error since user999 does not own the order created by user123
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authorized to reorder this order."}

# Ensure 404 is returned when trying to reorder an order that does not exist.
def test_reorder_past_order_returns_404_when_original_order_does_not_exist(setup_test_environment):
    reorder_request = {
        "card_id": "card-123"
    }

    reorder_response = client.post("/orders/reorder/nonexistent-order-id", json=reorder_request)
    assert reorder_response.status_code == 404
    assert reorder_response.json() == {"detail": "Original order not found."}

#Ensures that reorder allows changing delivery method and address, and validates required fields based on delivery method.
def test_reorder_past_order_allows_changing_delivery_method(setup_test_environment):
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantD",
        "delivery_method": "delivery",
        "delivery_address": "111 First St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Pasta", "price": 18.0}
        ]
    }

    create_response = client.post("/orders", json=original_order_request)
    assert create_response.status_code == 201

    original_order = create_response.json()
    original_order_id = original_order["order_id"]

    # Reorder with new delivery method and pickup location
    reorder_request = {
        "card_id": "card-123",
        "delivery_method": "pickup",
        "pickup_location": "Front Counter"
    }

    reorder_response = client.post(f"/orders/reorder/{original_order_id}", json=reorder_request)
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    #validate updated delivery method and pickup location in the new order, while other details remain the same
    assert reordered_order["order_id"] != original_order["order_id"]
    assert reordered_order["delivery_method"] == "pickup"
    assert reordered_order["pickup_location"] == "Front Counter"