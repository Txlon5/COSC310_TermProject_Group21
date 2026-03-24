from fastapi import HTTPException
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse



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


def calculate_order_subtotal(payload: SubtotalRequest, menu_items: list) -> SubtotalResponse:
    if not menu_items:
        raise HTTPException(status_code=404, detail="No menu items found for restaurant")

    menu_lookup = {str(item.menuItemId): item for item in menu_items}
    #sr1
    subtotal = calculate_subtotal(payload.items, menu_lookup)

    
    return SubtotalResponse(subtotal=subtotal)