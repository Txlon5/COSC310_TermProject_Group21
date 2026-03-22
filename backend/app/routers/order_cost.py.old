from fastapi import APIRouter
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse
from app.repositories.menu_repository import get_menu_items_by_restaurant
from app.services.order_cost_service import calculate_order_subtotal

router = APIRouter(prefix="/order-cost", tags=["Order Cost"])


@router.post("/subtotal", response_model=SubtotalResponse)
def calculate_subtotal_endpoint(payload: SubtotalRequest):
    
     #SR1 endpoint:Calculates the subtotal of the selected order items.
    
    menu_items = get_menu_items_by_restaurant(payload.restaurant_id)
    return calculate_order_subtotal(payload, menu_items)