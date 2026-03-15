from app.models.order import Order

orders_db = [
    Order(
        id=1,
        user_id=101,
        items=["Burger", "Fries"],
        total_price=18.99,
        delivery_method=None,
        delivery_address=None,
        pickup_location=None,
        assigned_driver=None,
        status="created"
    ),
    Order(
        id=2,
        user_id=102,
        items=["Pizza"],
        total_price=14.50,
        delivery_method=None,
        delivery_address=None,
        pickup_location=None,
        assigned_driver=None,
        status="created"
    )
]