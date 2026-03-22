from app.repositories.orders_repository import load_all, save_all
from app.schemas.order import Order
import pytest

from app.repositories.orders_repository import OrdersRepository


# Test that creating an order stores it in the repository
def test_create_order_stores_order():
    repo = load_all() # Quick instance to test the repository without needing to start the server
    
    # Create an order and check that it is stored correctly, values are arbitrary for testing purposes
    order = Order(
        restaurant_id="101", # Arbitrary value for testing, we just want to make sure the order is created and stored correctly in the repository; value doesn't need to be from csv/changed
        items=[{"menuItemId": 5, "quantity": 2}]
    )
    assert order is not None
    assert order["orderId"] == 1
    assert order["restaurant_id"] == 101
    assert len(repo.orders) == 1


def test_get_order_by_id_returns_correct_order():
    repo = OrdersRepository() # Quick instance to test the repository without needing to start the server
    
    # Create an order to ensure there is something in the repository to retrieve like above
    created = repo.create_order(
        restaurant_id=102,
        items=[{"menuItemId": 7, "quantity": 1}]
    )
    found = repo.get_order_by_id(created["orderId"])
    assert found is not None
    assert found["orderId"] == created["orderId"]
    
def test_update_completed_order_raises_error(): # feat4-sr2 test to ensure we cannot update a completed order
    repo = OrdersRepository()
    order = repo.create_order(
        restaurant_id=19,
        items=[{"menuItemId": 1, "quantity": 1}] # This is our order
    )
    repo.mark_order_status(order["orderId"], "completed") # And if we mark it as completed...
    with pytest.raises(ValueError):
        repo.update_order(order["orderId"], items=[{"menuItemId": 2, "quantity": 2}]) # We should hopefully get an error when trying to change its items