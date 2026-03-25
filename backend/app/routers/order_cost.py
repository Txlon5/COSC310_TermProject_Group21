from fastapi import APIRouter,HTTPException
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse
from app.services.menu_service import fetch_menu_by_restaurant_id
from app.services.order_cost_service import calculate_order_subtotal

router = APIRouter(prefix="/order-cost", tags=["Order Cost"])


@router.post("/subtotal", response_model=SubtotalResponse)
def calculate_subtotal_endpoint(payload: SubtotalRequest):
    if payload.delivery_method is not None:
        if payload.delivery_method not in ["delivery", "pickup"]:
            raise HTTPException(status_code=400,detail="delivery_method must be either 'delivery' or 'pickup'.")
     #SR1 endpoint:Calculates the subtotal of the selected order items.
    menu_items = fetch_menu_by_restaurant_id(payload.restaurant_id)
    return calculate_order_subtotal(payload, menu_items)