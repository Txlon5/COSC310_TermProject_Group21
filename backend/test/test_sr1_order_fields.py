from app.schemas.order import Order, OrderItem
from app.schemas.delivery import DeliveryStatus, DeliveryType
from datetime import datetime, timezone

def test_order_can_store_delivery_fields():
    now = datetime.now(timezone.utc)
    order = Order(
        order_id="test",
        user_id="101",
        restaurant_id="rest-1",
        items=[OrderItem(menuItemId= 1, quantity= 1, name= "Shawarma", price= 12.99)],
        total_price=12.99,
        delivery_method=DeliveryType("delivery"),
        delivery_address="123 Main St",
        pickup_location=None,
        assigned_driver="Alex",
        status=DeliveryStatus("ready"),
        created_at=now,
        updated_at=now,
        delivered_at=None
    )

    assert order.delivery_method == DeliveryType.delivery
    assert order.delivery_address == "123 Main St"
    assert order.pickup_location is None
    assert order.status == DeliveryStatus.ready
    assert order.assigned_driver == "Alex"
 

def test_order_can_store_pickup_fields():
    now = datetime.now(timezone.utc)
    order = Order(
        order_id="test",
        user_id="102",
        restaurant_id="rest-2",
        items=[OrderItem(menuItemId= 2, quantity= 1, name= "Pizza", price= 18.50)],
        total_price=18.50,
        delivery_method=DeliveryType("pickup"),
        delivery_address=None,
        pickup_location="Front Desk",
        status=DeliveryStatus("ready"),
        assigned_driver=None,
        created_at=now,
        updated_at=now,
        delivered_at=None
    )

    assert order.delivery_method == "pickup"
    assert order.delivery_address is None
    assert order.pickup_location == "Front Desk"
    assert order.status == DeliveryStatus.ready
    assert order.assigned_driver is None