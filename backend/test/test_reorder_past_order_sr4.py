import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.schemas.payment_transaction import PaymentStatusType
from app.services.notification_service import NotificationService
from app.schemas.payment_method import CreditCard

client = TestClient(app)
notification_service = NotificationService()


def setup_function():
    notification_service.clear_notifications()  # Clear notifications before each test 


def override_get_current_user():
    return User(
        id="user123",
        name="Test User",
        email="user@example.com",
        password="password123",
        role="user",
    )


@pytest.fixture
def setup_test_environment():
    # Force authenticated user for reorder endpoint
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Fake in-memory orders repository
    fake_db = []

    mock_menu_item1 = MagicMock()
    mock_menu_item1.menuItemId = 1

    mock_menu_item2 = MagicMock()
    mock_menu_item2.menuItemId = 2

    mock_menu = [mock_menu_item1, mock_menu_item2]

    def mock_load():
        return fake_db.copy()

    def mock_save(data):
        fake_db.clear()
        fake_db.extend(data)

    # Mock card details for the user
    mock_card = CreditCard(
        id="card-123",
        user_id="user123",
        card_num="12345678901234567",
        card_cvc="123",
        card_exp="2027-12",
        holder_name="Test User",
        holder_address="123 Test St",
    )
    

    with patch("app.services.orders_service.load_all", side_effect=mock_load), \
         patch("app.services.orders_service.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", side_effect=lambda restaurant_id: mock_menu), \
         patch("app.services.orders_service.get_card_for_user", return_value=mock_card), \
         patch("app.services.orders_service.create_transaction", return_value=PaymentStatusType.pending):
        yield {
            "fake_db": fake_db,
            "mock_menu": mock_menu,
        }

    app.dependency_overrides = {}


def create_original_order():
    original_order_request = {
        "user_id": "user123",
        "card_id": "card-123",
        "restaurant_id": "restaurant-1",
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        "items": [
            {"menuItemId": 1, "quantity": 1, "name": "Burger", "price": 10.99}
        ]
    }
    return client.post("/orders", json=original_order_request)

#Ensures error message is returned when user tries to reorder an order that does not exist, and that no new order or notification is created.
def test_reorder_returns_404_when_original_order_does_not_exist(setup_test_environment):
    response = client.post("/orders/reorder/nonexistent-order-id",json={"card_id": "card-123"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Original order not found."}

    # No order should be created
    assert len(setup_test_environment["fake_db"]) == 0

    # No notification is created
    notifications = notification_service.get_notifications_for_user("user123")
    assert len(notifications) == 0

#Ensures a reorder follow the same validation rules as creating a new order. If the original order contains an item that is no longer on the menu, the reorder should fail with a 400 error and appropriate message. 
# Also ensures that no new order or notification is created in this failed scenario.
def test_reorder_uses_existing_order_creation_validation_rules(setup_test_environment):
    create_response = create_original_order()
    assert create_response.status_code == 201
    original_order_id = create_response.json()["order_id"]

    # Remove the original menu item from the restaurant menu before reorder
    # This simulates restaurant/menu changes and proves reorder re-validates through create_order()
    setup_test_environment["mock_menu"].clear()
    remaining_menu_item = MagicMock()
    remaining_menu_item.menuItemId = 2
    setup_test_environment["mock_menu"].append(remaining_menu_item)

    response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123"})

    assert response.status_code == 400
    assert "Invalid menuItemId" in response.json()["detail"]

    # Only the original order should exist
    assert len(setup_test_environment["fake_db"]) == 1

    # Only the original order-created notification should exist
    notifications = notification_service.get_notifications_for_user("user123")
    assert len(notifications) == 1
    assert notifications[0].type == "Order_Created"
    assert notifications[0].order_id == original_order_id

# Ensures that if a reorder attempt fails validation, no new order is created and no new notification is generated.
def test_failed_reorder_does_not_create_new_order_or_notification(setup_test_environment):
    create_response = create_original_order()
    assert create_response.status_code == 201
    original_order_id = create_response.json()["order_id"]

    # Invalid reorder request: switching to pickup without pickup_location
    response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123","delivery_method": "pickup"})
    assert response.status_code == 400
    assert response.json() == {"detail": "pickup_location is required when delivery_method is 'pickup'."}

    # Still only the original order
    assert len(setup_test_environment["fake_db"]) == 1

    # Still only the original notification
    notifications = notification_service.get_notifications_for_user("user123")
    assert len(notifications) == 1
    assert notifications[0].order_id == original_order_id

#Ensures that a successful reorder creates a new order with a different order ID and generates a new notification for the new order, while the original order and its notification remain unchanged.
def test_successful_reorder_creates_notification_with_new_order_id_for_correct_user(setup_test_environment):
    create_response = create_original_order()
    assert create_response.status_code == 201
    original_order_id = create_response.json()["order_id"]

    notifications_before = notification_service.get_notifications_for_user("user123")
    assert len(notifications_before) == 1

    reorder_response = client.post(f"/orders/reorder/{original_order_id}",json={"card_id": "card-123"})
    assert reorder_response.status_code == 201
    
    reordered_order = reorder_response.json()
    new_order_id = reordered_order["order_id"]

    # New order must be different from original order
    assert new_order_id != original_order_id

    # Now two orders should exist
    assert len(setup_test_environment["fake_db"]) == 2

    # Notification should be generated for the new order
    notifications = notification_service.get_notifications_for_user("user123")
    assert len(notifications) == 2

    reorder_notification = notifications[1]
    assert reorder_notification.user_id == "user123"
    assert reorder_notification.order_id == new_order_id
    assert reorder_notification.type == "Order_Created"
    assert reorder_notification.title == "Order Created"
    assert reorder_notification.message == f"Your order {new_order_id} has been created successfully."
    assert reorder_notification.timestamp is not None