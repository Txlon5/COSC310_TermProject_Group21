import pytest
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import OrdersRepository


def test_service_creates_valid_order():
    service = OrdersService(OrdersRepository()) # Call the service with a fresh repository instance

    order = service.create_order(
        user_id=1,
        restaurant_id=101,
        items=[{"menuItemId": 5, "quantity": 2}]
    ) # Create an order with valid/arbitrary data

    assert order["orderId"] == 1 # Check that the order ID is assigned correctly
    assert len(order["items"]) == 1 # Check that the order contains the item we added


def test_service_rejects_empty_order(): # We have a requirement that an order must contain at least one item
    service = OrdersService(OrdersRepository())

    with pytest.raises(ValueError):
        service.create_order(
            user_id=1,
            restaurant_id=101,
            items=[]
        ) # So just ensure we riase an error if we try to create an order with no items but other valid data


def test_service_retrieves_created_order(): # Test that we can retrieve an order after creating it
    service = OrdersService(OrdersRepository())

    created = service.create_order(
        user_id=3,
        restaurant_id=201,
        items=[{"menuItemId": 9, "quantity": 1}]
    )

    fetched = service.get_order_by_id(created["orderId"])

    assert fetched["orderId"] == created["orderId"] # Check that the fetched order ID matches the created order ID