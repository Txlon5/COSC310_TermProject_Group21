from fastapi import APIRouter
from app.schemas.order_cost import SubtotalRequest, SubtotalResponse,OrderCostRequest,OrderCostResponse
from app.services.menu_service import fetch_menu_by_restaurant_id
from app.services.order_cost_service import calculate_order_subtotal, calculate_order_cost

router = APIRouter(prefix="/order-cost", tags=["Order Cost"])


@router.post("/subtotal", response_model=SubtotalResponse)
def calculate_subtotal_endpoint(payload: SubtotalRequest):
    
     #SR1 endpoint:Calculates the subtotal of the selected order items.
    menu_items = fetch_menu_by_restaurant_id(payload.restaurant_id)
    return calculate_order_subtotal(payload, menu_items)

# SR2
@router.post("/calculate", response_model=OrderCostResponse)
def calculate_order_cost_endpoint(payload: OrderCostRequest):
    menu_items = fetch_menu_by_restaurant_id(payload.restaurant_id)
    return calculate_order_cost(payload, menu_items)