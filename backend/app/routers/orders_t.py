from fastapi import APIRouter, HTTPException
from app.schemas.orders_t import CreateOrderRequest, CreateOrderResponse, OrderStatusUpdateRequest, DeliveryInfoUpdateRequest, OrderOut
from app.services.orders_service import OrdersService
from app.repositories.orders_repository import OrdersRepository
from app.repositories.restaurants_repository import RestaurantsRepository

router = APIRouter()

# Initialize OrdersService with repositories
orders_service = OrdersService(OrdersRepository(), RestaurantsRepository())

@router.post("/orders", response_model=CreateOrderResponse)
def create_order_endpoint(order: CreateOrderRequest):
    order_data = order.dict()
    created_order = orders_service.create_order(order_data["restaurant_id"], order_data["items"])
    # Get restaurant name and menu items
    restaurants_repo = RestaurantsRepository()
    restaurants = restaurants_repo.get_all()
    restaurant = next((r for r in restaurants if r["restaurantId"] == created_order["restaurantId"]), None)
    restaurant_name = restaurant["name"] if restaurant else None
    menu_items = restaurant["menuItems"] if restaurant else []
    # Add item_name to each item
    items_with_names = []
    for item in created_order["items"]:
        item_name = next((m["name"] for m in menu_items if m["menuItemId"] == item["menuItemId"]), None)
        item_with_name = dict(item)
        item_with_name["item_name"] = item_name
        items_with_names.append(item_with_name)
    response_data = {
        "order_id": str(created_order["orderId"]),
        "user_id": order_data.get("user_id"),
        "restaurantId": created_order["restaurantId"],
        "restaurant_name": restaurant_name,
        "items": items_with_names,
        "status": "Created"
    }
    return CreateOrderResponse.model_validate(response_data)

@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order_endpoint(order_id: str):
    try:
        order = orders_service.get_order_by_id(int(order_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(
        order_id=order["orderId"],
        restaurant_id=order["restaurantId"],
        items=order["items"]
    )

@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status_endpoint(order_id: str, status_update: OrderStatusUpdateRequest):
    # Placeholder: OrdersService does not have update_order_status yet
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/orders/{order_id}/delivery", response_model=OrderOut)
def assign_delivery_info_endpoint(order_id: str, delivery_info: DeliveryInfoUpdateRequest):
    # Placeholder: OrdersService does not have assign_delivery_info yet
    raise HTTPException(status_code=501, detail="Not implemented")
