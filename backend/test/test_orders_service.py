from datetime import datetime, timezone
import pytest
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import save_all
from app.repositories.restaurants_repository import RestaurantsRepository
from app.schemas.order import CreateOrderRequest, OrderItem,DeliveryInfoUpdateRequest, OrderStatusUpdateRequest
from app.schemas.user import User
from fastapi import HTTPException
from app.schemas.delivery import DeliveryStatus, DeliveryType
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.payment_method import CreditCard
from app.schemas.payment_transaction import PaymentStatusType, PaymentTransaction

client = TestClient(app)

# Use a restaurant id that exists in the packaged restaurant data.
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

def seed_restaurant():
    repo = RestaurantsRepository()
    repo.save_all([
        {
            "restaurant_id": RESTAURANT_ID,
            "restaurant_name": "Test Pizza",
            "tags": ["pizza"],
            "isOpen": True,
            "menuItems": [
                {"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "category": "Food"},
                {"menuItemId": 2, "name": "Cheesey Bread", "price": 15.0, "category": "Food"},
                {"menuItemId": 3, "name": "Canadian Pizza", "price": 23.0, "category": "Food"}
            ]
        }
    ])

# Create test declined_payment for test
def _make_declined_transaction(order_id, user_id):
    return PaymentTransaction(
        payment_id="pay-1",
        order_id=order_id,
        user_id=user_id,
        card=CreditCard(
            id="card-1",
            user_id=user_id,
            card_num="4111111111111111",
            card_cvc="123",
            card_exp="2030-01",
            holder_name="Test User",
            holder_address="1 Test St",
        ),
        status=PaymentStatusType.declined,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        price_total=0.0,
    )


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
    seed_restaurant()
    
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
    seed_restaurant()

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
    
#////////////////

def test_list_orders_simple():
    save_all([
        {
            "order_id": "order-1",
            "user_id": "user-1",
            "restaurant_id": RESTAURANT_ID,
            "items": [
                {
                    "menuItemId": 1,
                    "name": "Pizza",
                    "price": 10.0,
                    "quantity": 1
                }
            ],
            "status": "created",
            "delivery_method": "delivery",
            "delivery_address": None,
            "pickup_location": None,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "delivered_at": None
        }
    ])

    service = OrdersService()
    orders = service.list_orders()

    assert len(orders) == 1
    assert orders[0].order_id == "order-1"


def test_create_order_bad_menu_item():
    service = OrdersService()

    with pytest.raises(HTTPException) as exc_info:
        service.create_order(
            CreateOrderRequest(
                user_id="user-1",
                card_id="test-card-id",
                restaurant_id=RESTAURANT_ID,
                items=[OrderItem(menuItemId=999, name="Fake", price=1.0, quantity=1)]
            )
        )

    assert exc_info.value.status_code == 400


def test_create_order_zero_quantity():
    service = OrdersService()

    with pytest.raises(HTTPException) as exc_info:
        service.create_order(
            CreateOrderRequest(
                user_id="user-1",
                card_id="test-card-id",
                restaurant_id=RESTAURANT_ID,
                items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=0)]
            )
        )

    assert exc_info.value.status_code == 400


def test_assign_delivery_info_not_found():
    service = OrdersService()

    with pytest.raises(HTTPException) as exc_info:
        service.assign_delivery_info(
            "missing-id",
            DeliveryInfoUpdateRequest(
                delivery_method=DeliveryType.pickup,
                pickup_location="Front Desk"
            )
        )

    assert exc_info.value.status_code == 404


def test_update_order_info_not_found():
    service = OrdersService()

    with pytest.raises(HTTPException) as exc_info:
        service.update_order_info(
            "missing-id",
            [OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
        )

    assert exc_info.value.status_code == 404

# Update Order Status - Invalid Transition
def test_update_order_status_invalid_transition():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="card-1",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))

    # Make order go from created to complete
    with pytest.raises(HTTPException) as exc_info:
        service.update_order_status(
            order.order_id,
            OrderStatusUpdateRequest(status=DeliveryStatus.complete)
        )

    assert exc_info.value.status_code == 400

# Assign Delivery Info - Completed Order
def test_assign_delivery_info_completed_order():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="card-1",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))

    # Cancel order
    service.update_order_status(order.order_id, OrderStatusUpdateRequest(status=DeliveryStatus.cancelled))

    with pytest.raises(HTTPException) as exc_info:
        service.assign_delivery_info(
            order.order_id,
            DeliveryInfoUpdateRequest(delivery_method=DeliveryType.delivery)
        )

    assert exc_info.value.status_code == 400


# Assign Delivery Info - Pickup Location Valid
def test_assign_delivery_info_with_pickup_location():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="card-1",
        restaurant_id=RESTAURANT_ID,
        delivery_method=DeliveryType.pickup,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))

    updated = service.assign_delivery_info(
        order.order_id,
        DeliveryInfoUpdateRequest(pickup_location="Front Lobby")
    )

    assert updated.pickup_location == "Front Lobby"

# Update Order Info - Valid
def test_update_order_info_success():
    service = OrdersService()
    order = service.create_order(CreateOrderRequest(
        user_id="user-1",
        card_id="card-1",
        restaurant_id=RESTAURANT_ID,
        items=[OrderItem(menuItemId=1, name="Pizza", price=10.0, quantity=1)]
    ))

    updated = service.update_order_info(
        order.order_id,
        [OrderItem(menuItemId=2, name="Cheesey Bread", price=15.0, quantity=2)]
    )

    assert len(updated.items) == 1
    assert updated.items[0].menuItemId == 2