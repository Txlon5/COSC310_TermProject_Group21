from app.models.order import Order


def test_order_can_store_delivery_fields():
    order = Order(
        id=1,
        user_id=101,
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