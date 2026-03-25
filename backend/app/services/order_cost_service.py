from fastapi import HTTPException
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse, OrderCostRequest,OrderCostResponse
from typing import Optional

BC_TAX_RATE = 0.12


def round_money(value: float) -> float:
    return round(value + 1e-8, 2)


def calculate_subtotal(items, menu_lookup: dict) -> float:
    subtotal = 0.0

    for item in items:
        item_id = str(item.item_id)

        if item_id not in menu_lookup:
            raise HTTPException(status_code=404,detail=f"Menu item {item_id} not found")

        subtotal += menu_lookup[item_id].price * item.quantity

    return round_money(subtotal)


# SR1
def calculate_order_subtotal(payload: SubtotalRequest, menu_items: list) -> SubtotalResponse:
    if not menu_items:
        raise HTTPException(status_code=404, detail="No menu items found for restaurant")

    menu_lookup = {str(item.menuItemId): item for item in menu_items}
    subtotal = calculate_subtotal(payload.items, menu_lookup)

    return SubtotalResponse(subtotal=subtotal)


# SR2
def calculate_delivery_fee(delivery_method: Optional[str], distance_km: float = 0.0) -> float:
    if delivery_method == "pickup":
        return 0.0

    if delivery_method == "delivery":
        if distance_km <= 5:
            return 3.99
        elif distance_km <= 10:
            return 5.99
        else:
            return 7.99

    raise HTTPException(status_code=400, detail="Invalid delivery method")


def calculate_tax(subtotal: float, delivery_fee: float, province: str = "BC") -> float:
    tax_rates = {
        "BC": 0.12,
        "AB": 0.05,
        "ON": 0.13
    }

    rate = tax_rates.get(province, BC_TAX_RATE)
    return round_money((subtotal + delivery_fee) * rate)


def calculate_total(subtotal: float, delivery_fee: float, tax: float) -> float:
    return round_money(subtotal + delivery_fee + tax)


def calculate_order_cost(payload: OrderCostRequest, menu_items: list) -> OrderCostResponse:
    if not menu_items:
        raise HTTPException(status_code=404, detail="No menu items found for restaurant")

    if payload.delivery_method == "delivery" and not payload.delivery_address:
        raise HTTPException(status_code=400,detail="Delivery address is required for delivery orders")

    menu_lookup = {str(item.menuItemId): item for item in menu_items}

    subtotal = calculate_subtotal(payload.items, menu_lookup)

    distance = payload.distance_km or 0.0
    province = payload.province or "BC"

    delivery_fee = calculate_delivery_fee(payload.delivery_method, distance)
    tax = calculate_tax(subtotal, delivery_fee, province)
    total = calculate_total(subtotal, delivery_fee, tax)

    return OrderCostResponse(subtotal=subtotal,delivery_fee=delivery_fee,tax=tax,total=total)
