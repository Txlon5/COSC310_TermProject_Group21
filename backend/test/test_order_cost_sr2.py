import pytest
from fastapi import HTTPException
from app.schemas.order_cost import OrderCostRequest, OrderItemRequest
from app.services.order_cost_service import calculate_order_cost


class FakeMenuItem:
    def __init__(self, menuItemId, name, price, category):
        self.menuItemId = menuItemId
        self.name = name
        self.price = price
        self.category = category


def fake_menu():
    return [
        FakeMenuItem(1, "Burger", 8.99, "Food"),
        FakeMenuItem(2, "Fries", 3.99, "Food"),
    ]




def test_delivery_order_under_5km():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="delivery",
        delivery_address="123 Test St",
        province="BC",
        distance_km=4,
        items=[
            OrderItemRequest(item_id="1", quantity=1),
            OrderItemRequest(item_id="2", quantity=1),
        ]
    )

    result = calculate_order_cost(payload, fake_menu())

    assert result.subtotal == 12.98
    assert result.delivery_fee == 3.99
    assert result.tax == 2.04
    assert result.total == 19.01


def test_delivery_order_over_10km():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="delivery",
        delivery_address="Far Away",
        province="BC",
        distance_km=12,
        items=[
            OrderItemRequest(item_id="1", quantity=2),
        ]
    )

    result = calculate_order_cost(payload, fake_menu())

    assert result.subtotal == 17.98
    assert result.delivery_fee == 7.99
    assert result.tax == 3.12
    assert result.total == 29.09


def test_pickup_order():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="pickup",
        province="BC",
        distance_km=0,
        items=[
            OrderItemRequest(item_id="1", quantity=2),
        ]
    )

    result = calculate_order_cost(payload, fake_menu())

    assert result.subtotal == 17.98
    assert result.delivery_fee == 0.0
    assert result.tax == 2.16
    assert result.total == 20.14


def test_tax_changes_by_province():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="pickup",
        province="AB",
        distance_km=0,
        items=[
            OrderItemRequest(item_id="1", quantity=1),
        ]
    )

    result = calculate_order_cost(payload, fake_menu())

    assert result.tax == 0.45  # 5%



def test_empty_menu_items():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="pickup",
        items=[OrderItemRequest(item_id="1", quantity=1)]
    )

    with pytest.raises(HTTPException) as exc:
        calculate_order_cost(payload, [])

    assert exc.value.status_code == 404


def test_missing_delivery_address():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="delivery",
        items=[OrderItemRequest(item_id="1", quantity=1)]
    )

    with pytest.raises(HTTPException) as exc:
        calculate_order_cost(payload, fake_menu())

    assert exc.value.status_code == 400
    assert "delivery address" in exc.value.detail.lower()


def test_invalid_delivery_method():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="invalid",
        delivery_address="123",
        items=[OrderItemRequest(item_id="1", quantity=1)]
    )

    with pytest.raises(HTTPException) as exc:
        calculate_order_cost(payload, fake_menu())

    assert exc.value.status_code == 400


def test_menu_item_not_found():
    payload = OrderCostRequest(
        restaurant_id="test",
        delivery_method="pickup",
        items=[OrderItemRequest(item_id="999", quantity=1)]
    )

    with pytest.raises(HTTPException) as exc:
        calculate_order_cost(payload, fake_menu())

    assert exc.value.status_code == 404

