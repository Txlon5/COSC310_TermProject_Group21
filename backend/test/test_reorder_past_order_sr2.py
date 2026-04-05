import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.services.notification_service import NotificationService
from app.schemas.payment_method import CreditCard
from app.schemas.payment_transaction import PaymentStatusType


client = TestClient(app)
notification = NotificationService() 


def setup_function():
    notification.clear_notifications()      # Clear notifications before each test


# Mock user (normal)
def override_get_current_user():
    return User(
        id="user123",
        name="Test User",
        email="user@example.com",
        password="password123!",
        role="user"
    )


# Mock admin user
def override_get_current_user_admin():
    return User(
        id="admin123",
        name="Admin User",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )


# This fixture runs before every test automatically
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Override authentication to always return a test user
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Fake in-memory databases
    fake_orders_db = []
    fake_cards_db = [
        {
            "id": "test-card-id",
            "user_id": "user123",
            "card_num": "4111111111111111",
            "card_cvc": "123",
            "card_exp": "2027-12",
            "holder_name": "Test User",
            "holder_address": "123 Main St"
        }
    ]
    fake_transactions_db = []

    # Mock menu items to pass validation in create_order
    mock_menu_item1 = MagicMock()
    mock_menu_item1.menuItemId = 1

    mock_menu_item2 = MagicMock()
    mock_menu_item2.menuItemId = 2

    # Mock database load/save functions
    def mock_load_orders():
        return fake_orders_db.copy()

    def mock_save_orders(data):
        fake_orders_db.clear()
        fake_orders_db.extend(data)

    def mock_load_cards():
        return fake_cards_db.copy()

    def mock_load_transactions():
        return fake_transactions_db.copy()

    def mock_save_transactions(data):
        fake_transactions_db.clear()
        fake_transactions_db.extend(data)

    # Patch all external dependencies used in order creation.
    with patch("app.services.orders_service.load_all", side_effect=mock_load_orders), \
         patch("app.services.orders_service.save_all", side_effect=mock_save_orders), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item1, mock_menu_item2]), \
         patch("app.services.payments_service.card_repo.load_all", side_effect=mock_load_cards), \
         patch("app.services.payments_service.transaction_repo.load_all", side_effect=mock_load_transactions), \
         patch("app.services.payments_service.transaction_repo.save_all", side_effect=mock_save_transactions):
        yield

    # Clear overrides after test
    app.dependency_overrides = {}

#Ensures that the reorder endpoint correctly copies the restaurant_id and items list from the original order, and that each item preserves its details.
def test_reorder_past_order_copies_same_restaurant_id(setup_test_environment):
    #Create an original order to reorder from
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantA",
        "delivery_method": "delivery",
        "delivery_address": "123 Main St",
        "items": [
            {"menuItemId": 1, "quantity": 2, "name": "Burger", "price": 10.0}
        ]
    }

    create_response = client.post("/orders", json=original_order_request)
    assert create_response.status_code == 201

    original_order = create_response.json()
    original_order_id = original_order["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123"})
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    assert reordered_order["restaurant_id"] == original_order["restaurant_id"]

#Ensures that the reorder endpoint creates a new order with the same items list as the original order, and that each item preserves its details.
def test_reorder_past_order_copies_same_items_list(setup_test_environment):
    #Create an original order to reorder from
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantB",
        "delivery_method": "delivery",
        "delivery_address": "456 Oak Ave",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Pizza", "price": 15.0},
            {"menuItemId": 2, "quantity": 3, "name": "Fries", "price": 5.0}
        ]
    }

    create_response = client.post("/orders", json=original_order_request)
    assert create_response.status_code == 201

    original_order = create_response.json()
    original_order_id = original_order["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123"})
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()

    assert reordered_order["items"] == original_order["items"]

#Ensures that each item in the reordered order preserves its menuItemId, name, price, and quantity from the original order.
def test_reorder_past_order_preserves_each_item_detail(setup_test_environment):
    #Create an original order to reorder from
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurantC",
        "delivery_method": "delivery",
        "delivery_address": "789 Pine Rd",
        "items": [
            {"menuItemId": 1, "quantity": 2, "name": "Shawarma", "price": 12.0},
            {"menuItemId": 2, "quantity": 1, "name": "Drink", "price": 3.5}
        ]
    }

    create_response = client.post("/orders", json=original_order_request)
    assert create_response.status_code == 201

    original_order_id = create_response.json()["order_id"]

    reorder_response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123"})
    assert reorder_response.status_code == 201

    reordered_order = reorder_response.json()
    items = reordered_order["items"]

    # First item preserved correctly
    assert items[0]["menuItemId"] == 1
    assert items[0]["name"] == "Shawarma"
    assert items[0]["price"] == 12.0
    assert items[0]["quantity"] == 2

    # Second item preserved correctly
    assert items[1]["menuItemId"] == 2
    assert items[1]["name"] == "Drink"
    assert items[1]["price"] == 3.5
    assert items[1]["quantity"] == 1