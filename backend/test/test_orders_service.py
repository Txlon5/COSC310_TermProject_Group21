import pytest
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import OrdersRepository
from app.repositories.restaurants_repository import RestaurantsRepository

def test_service_creates_valid_order():
    service = OrdersService(OrdersRepository(), RestaurantsRepository())
    order = service.create_order(
        restaurant_id=19,
        items=[{"menuItemId": 5, "quantity": 2, "item_name": "Pasta"}]
    ) # Updated values to match the CSV file, also done for other tests in this file
    assert order["orderId"] == 1
    assert len(order["items"]) == 1

def test_service_rejects_empty_order():
    service = OrdersService(OrdersRepository(), RestaurantsRepository())
    with pytest.raises(ValueError): # We expect a ValueError to be raised when trying to create an order with no items
        service.create_order(
            restaurant_id=19,
            items=[]
        )

def test_service_retrieves_created_order():
    service = OrdersService(OrdersRepository(), RestaurantsRepository())
    created = service.create_order(
        restaurant_id=22,
        items=[{"menuItemId": 2, "quantity": 1, "item_name": "Burger"}]
    )
    fetched = service.get_order_by_id(created["orderId"]) # We should be able to retrieve the same order we just created
    assert fetched["orderId"] == created["orderId"] # The IDs should match, confirming we retrieved the correct order