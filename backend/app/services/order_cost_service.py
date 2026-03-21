from fastapi import HTTPException
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse
from typing import Optional

BC_TAX_RATE = 0.12

def round_money(value: float) -> float:
    return round(value + 1e-8, 2)


def calculate_subtotal(items, menu_lookup: dict) -> float:
    subtotal = 0.0

    for item in items:
        item_id = str(item.item_id)
        quantity = item.quantity

        if item_id not in menu_lookup:
            raise HTTPException(
                status_code=404,detail=f"Menu item {item_id} not found")

        price = menu_lookup[item_id].price
        subtotal += price * quantity

    return round_money(subtotal)
    #sr2
def calculate_delivery_fee(delivery_method: Optional[str]) -> float:
    if delivery_method == "delivery":
        return 4.99
    return 0.0


def calculate_tax(subtotal: float, delivery_fee: float) -> float:
    return round_money((subtotal + delivery_fee) * BC_TAX_RATE)


def calculate_total(subtotal: float, delivery_fee: float, tax: float) -> float:
    return round_money(subtotal + delivery_fee + tax)


def calculate_order_subtotal(payload: SubtotalRequest, menu_items: list) -> SubtotalResponse:
    if not menu_items:
        raise HTTPException(status_code=404, detail="No menu items found for restaurant")

    menu_lookup = {str(item.id): item for item in menu_items}
    #sr1
    subtotal = calculate_subtotal(payload.items, menu_lookup)

    #sr2
    delivery_fee = calculate_delivery_fee(payload.delivery_method)
    tax = calculate_tax(subtotal, delivery_fee)
    total = calculate_total(subtotal, delivery_fee, tax)
    return SubtotalResponse(subtotal=subtotal,delivery_fee=delivery_fee,tax=tax,total=total)