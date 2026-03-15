from app.models.order import Order

orders_db = [
    Order(
        id=1,
        user_id="101",
        items=["Burger"],
        total_price=12.99,
        delivery_method="delivery",
        delivery_address="123 Main St",
        pickup_location=None,
        assigned_driver="Alex"
    ),
    Order(
        id=2,
        user_id="102",
        items=["Pizza"],
        total_price=18.50,
        delivery_method="pickup",
        delivery_address=None,
        pickup_location="Front Desk",
        assigned_driver=None
    )
]