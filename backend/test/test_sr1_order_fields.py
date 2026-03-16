from app.models.order import Order


def test_order_can_store_delivery_fields():
    order = Order(
        id=1,
        user_id="101",
        items=["Burger"],
        total_price=12.99,
        delivery_method="delivery",
        delivery_address="123 Main St",
        pickup_location=None,
        assigned_driver="Alex"
    )

    assert order.delivery_method == "delivery"
    assert order.delivery_address == "123 Main St"
    assert order.pickup_location is None
    assert order.assigned_driver == "Alex"


def test_order_can_store_pickup_fields():
    order = Order(
        id=2,
        user_id="102",
        items=["Pizza"],
        total_price=18.50,
        delivery_method="pickup",
        delivery_address=None,
        pickup_location="Front Desk",
        assigned_driver=None
    )

    assert order.delivery_method == "pickup"
    assert order.delivery_address is None
    assert order.pickup_location == "Front Desk"
    assert order.assigned_driver is None