import pytest
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import save_all
from app.schemas.order import CreateOrderRequest, OrderItem
from app.schemas.user import User
from fastapi import HTTPException

# Use a restaurant id that exists in the packaged restaurant data.
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"


def setup_function():
    # Start every test with no saved orders.
    save_all([])


def test_service_creates_valid_order():
    service = OrdersService()

    # Create a valid order and verify important fields were saved correctly.
    order = service.create_order(
        CreateOrderRequest(
            user_id="user-1",
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
        service.create_order(CreateOrderRequest(user_id="user-1", restaurant_id=RESTAURANT_ID, items=[]))


def test_service_retrieves_created_order_for_matching_user():
    service = OrdersService()
    created = service.create_order(
        CreateOrderRequest(
            user_id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
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
            restaurant_id=RESTAURANT_ID,
            items=[OrderItem(menuItemId=3, name="Canadian Pizza", price=23.0, quantity=1)],
        )
    )
    other_user = User(id="other-id", name="Other", email="other@example.com", password="hashed", role="user")

    # A different user should get a forbidden error.
    with pytest.raises(HTTPException) as exc_info:
        service.get_order_by_id(created.order_id, other_user)

    assert exc_info.value.status_code == 403






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