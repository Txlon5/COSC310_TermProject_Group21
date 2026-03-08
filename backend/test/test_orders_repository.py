from app.repositories.orders_repository import OrdersRepository


# Test that creating an order stores it in the repository
def test_create_order_stores_order():
    repo = OrdersRepository() # Quick instance to test the repository without needing to start the server
    
    # Create an order and check that it is stored correctly, values are arbitrary for testing purposes
    order = repo.create_order(
        user_id=1,
        restaurant_id=101,
        items=[{"menuItemId": 5, "quantity": 2}]
    )

    # Some basic assertions to check that the order was created and stored correctly
    assert order is not None
    assert order["orderId"] == 1
    assert order["userId"] == 1
    assert order["restaurantId"] == 101
    assert len(repo.orders) == 1


def test_get_order_by_id_returns_correct_order():
    repo = OrdersRepository() # Quick instance to test the repository without needing to start the server
    
    # Create an order to ensure there is something in the repository to retrieve like above
    created = repo.create_order(
        user_id=2,
        restaurant_id=102,
        items=[{"menuItemId": 7, "quantity": 1}]
    )

    found = repo.get_order_by_id(created["orderId"]) # Try to retrieve the order we just created

    assert found is not None # Check that we found something
    assert found["orderId"] == created["orderId"] # Check that the order ID matches