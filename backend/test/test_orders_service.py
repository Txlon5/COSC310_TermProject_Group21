import pytest
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import save_all
from app.schemas.order import CreateOrderRequest, OrderItem
from app.schemas.user import User
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Use a restaurant id that exists in the packaged restaurant data.
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

# Making sure we don't override the orders JSON file
# Automatic fixture to isolate tests, it runs per test 
@pytest.fixture(autouse=True)
def isolated_orders(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.orders_repository.DATA_PATH", tmp_path / "orders.json")
    save_all([])


def test_service_creates_valid_order():
    service = OrdersService()

    # Create a valid order and verify important fields were saved correctly.
    order = service.create_order(
        CreateOrderRequest(
            user_id="user-1",
            card_id="test-card-id",
            restaurant_id=RESTAURANT_ID,
            items=[OrderItem(menuItemId=1, name="Onion Pizza", price=26.0, quantity=2)],
        )
    )

    assert order.user_id == "user-1"
    assert order.restaurant_id == RESTAURANT_ID
    assert len(order.items) == 1
    assert order.items[0].menuItemId == 1


def test_service_rejects_empty_order():
    service = OrdersService()

    # Empty item lists are not allowed.
    with pytest.raises(ValueError):
        service.create_order(CreateOrderRequest(user_id="user-1", card_id="test-card-id", restaurant_id=RESTAURANT_ID, items=[]))


def test_create_order_rejects_no_items():
    service = OrdersService()
    with pytest.raises(ValueError) as exc_info:
        service.create_order(
            CreateOrderRequest(
                user_id="user-1",
                card_id="test-card-id",
                restaurant_id=RESTAURANT_ID,
                items=[]
            )
        )
    assert "Order must contain at least one item" in str(exc_info.value)


def test_service_retrieves_created_order_for_matching_user():
    service = OrdersService()
    created = service.create_order(
        CreateOrderRequest(
            user_id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
            card_id="test-card-id",
            restaurant_id=RESTAURANT_ID,
            items=[OrderItem(menuItemId=2, name="Cheesey Bread", price=15.0, quantity=1)],
        )
    )
    current_user = User(
        id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        name="Jane Doe",
        email="jane.doe@example.com",
        password="hashed",
        role="user",
    )

    # The order owner should be able to fetch their own order.
    fetched = service.get_order_by_id(created.order_id, current_user)
    assert fetched.order_id == created.order_id


def test_service_rejects_access_for_wrong_user():
    service = OrdersService()
    created = service.create_order(
        CreateOrderRequest(
            user_id="owner-id",
            card_id="test-card-id",
            restaurant_id=RESTAURANT_ID,
            items=[OrderItem(menuItemId=3, name="Canadian Pizza", price=23.0, quantity=1)],
        )
    )
    other_user = User(id="other-id", name="Other", email="other@example.com", password="hashed", role="user")

    # A different user should get a forbidden error.
    with pytest.raises(HTTPException) as exc_info:
        service.get_order_by_id(created.order_id, other_user)

    assert exc_info.value.status_code == 403


def test_get_order_by_id_owner():
    service = OrdersService()
    # Create and save an order
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="test-card-id",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))
    user = User(id="user-1", name="Test", email="test@example.com", password="pw", role="user")
    result = service.get_order_by_id(order.order_id, user)
    assert result.order_id == order.order_id


def test_get_order_by_id_admin():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="test-card-id",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))
    admin = User(id="admin-id", name="Admin", email="admin@example.com", password="pw", role="admin")
    result = service.get_order_by_id(order.order_id, admin)
    assert result.order_id == order.order_id


def test_get_order_by_id_forbidden():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="test-card-id",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))
    other_user = User(id="user-2", name="Other", email="other@example.com", password="pw", role="user")
    with pytest.raises(HTTPException) as exc_info:
        service.get_order_by_id(order.order_id, other_user)
    assert exc_info.value.status_code == 403


def test_get_order_by_id_not_found():
    service = OrdersService()
    user = User(id="user-1", name="Test", email="test@example.com", password="pw", role="user")
    with pytest.raises(HTTPException) as exc_info:
        service.get_order_by_id("nonexistent-id", user)
    assert exc_info.value.status_code == 404




def test_subtotal_endpoint_works():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "items": [
            {
                "item_id": "1",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/subtotal", json=payload)

    assert response.status_code == 200
    assert "subtotal" in response.json()


def test_calculate_endpoint_works():
    payload = {
        "restaurant_id": RESTAURANT_ID,
        "delivery_method": "delivery",
        "delivery_address": "123 Test St",
        "province": "BC",
        "distance_km": 4,
        "items": [
            {
                "item_id": "1",
                "quantity": 1
            }
        ]
    }

    response = client.post("/order-cost/calculate", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert "subtotal" in data
    assert "delivery_fee" in data
    assert "tax" in data
    assert "total" in data
    
    
# LEGACY CODE BELOW - FOR REFERENCE
# def test_service_creates_valid_order():
#     service = OrdersService(OrdersRepository(), RestaurantsRepository())
#     order = service.create_order(
#         restaurant_id=19,
#         items=[{"menuItemId": 5, "quantity": 2, "item_name": "Pasta"}]
#     ) # Updated values to match the CSV file, also done for other tests in this file
#     assert order["orderId"] == 1
#     assert len(order["items"]) == 1

# def test_service_rejects_empty_order():
#     service = OrdersService(OrdersRepository(), RestaurantsRepository())
#     with pytest.raises(ValueError): # We expect a ValueError to be raised when trying to create an order with no items
#         service.create_order(
#             restaurant_id=19,
#             items=[]
#         )

# def test_service_retrieves_created_order():
#     service = OrdersService(OrdersRepository(), RestaurantsRepository())
#     created = service.create_order(
#         restaurant_id=22,
#         items=[{"menuItemId": 2, "quantity": 1, "item_name": "Burger"}]
#     )
#     fetched = service.get_order_by_id(created["orderId"]) # We should be able to retrieve the same order we just created
#     assert fetched["orderId"] == created["orderId"] # The IDs should match, confirming we retrieved the correct order
