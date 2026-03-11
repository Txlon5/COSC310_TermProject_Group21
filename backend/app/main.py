from fastapi import FastAPI, HTTPException, Query, Body

# RESTAURANT STUFF - I am unsure if we will put all imports and such in main?
from app.data.restaurants_data import RESTAURANTS
from typing import List, Optional
from app.schemas.restaurants import RestaurantOut
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService
# END Restaurant imports

app = FastAPI()

@app.get("/")
def hello():
    return {"msg": "Hello World"}

@app.get("/items/{name}")
def get_item(name: str):
    return {"item": name, "status": "ok"}

@app.get("/debug")
def debug_data():
    return RESTAURANTS # Trying to see if I can get a response from RESTAURANTS

# Create repository instance
# This object is responsible for retrieving restaurant data
restaurants_repository = RestaurantsRepository()

# Inject repository into the service
# The service will call the repository internally
restaurants_service = RestaurantsService(restaurants_repository)

# Using the endpoint, response_model ensures returned data matches RestaurantOut schema
@app.get("/restaurants", response_model=List[RestaurantOut])
def get_restaurants(    
                    q: Optional[str] = Query(default=None),
                    restaurantId: Optional[int] = Query(default=None, ge=1),
                    isOpen: Optional[bool] = Query(default=None),
                    tag: Optional[str] = Query(default=None),
                    page: Optional[int] = Query(default=None, ge=1), # Where ge is greater than or equal to, so we make sure the page number is valid
                    pageSize: Optional[int] = Query(default=None, ge=1),
                    ):
    
    # SR2 - Implementing search and filter functionality
    try:
        # If no params were supplied, behave like SR1 - it's the same functionality it just looks a bit different
        if q is None and restaurantId is None and isOpen is None and tag is None and page is None and pageSize is None:
            return restaurants_service.get_restaurants()
        
        # Apply the provided filters and search accordingly, and the logic is handled in the service.
        return restaurants_service.search_restaurants(
            q=q,
            restaurant_id=restaurantId,
            is_open=isOpen,
            tag=tag,
            page=page,
            page_size=pageSize,
        )
        
    except ValueError as e:
        # “handled gracefully with an error message” as put in our acceptance criteria, 
        # so we catch the ValueError from the service and return a 400 Bad Request with the error message
        raise HTTPException(status_code=400, detail=str(e))

"""Feat 4 Stuff - Will move to router soon"""
# Orders imports
from app.schemas.orders import OrderCreateRequest, OrderOut
from app.repositories.orders_repository import OrdersRepository
from app.services.orders_service import OrdersService

# Create orders repository and service
orders_repository = OrdersRepository()
orders_service = OrdersService(orders_repository, restaurants_repository)

# Orders endpoint
@app.post("/orders")
def create_order(order: OrderCreateRequest):
    try:
        # Convert items to dicts for validation
        items = [item.dict() for item in order.items]
        created = orders_service.create_order(order.restaurantId, items)
        # Lookup item names from restaurant menu
        restaurants = restaurants_repository.get_all()
        restaurant = next((r for r in restaurants if r["restaurantId"] == order.restaurantId), None)
        menu_lookup = {item["menuItemId"]: item["name"] for item in restaurant["menuItems"]} if restaurant else {}
        enriched_items = []
        for item in items:
            enriched_items.append({
                "menuItemId": item["menuItemId"],
                "name": menu_lookup.get(item["menuItemId"], "Unknown"),
                "quantity": item["quantity"]
            })
        return {
            "orderId": created["orderId"],
            "restaurantId": created["restaurantId"],
            "items": enriched_items
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Additional order endpoint
@app.put("/orders/{orderId}")
def update_order(orderId: int, restaurantId: int = None, items: List[dict] = Body(default=None)):
    try:
        updated = orders_repository.update_order(orderId, restaurant_id=restaurantId, items=items)
        return {
            "orderId": updated["orderId"],
            "restaurantId": updated["restaurantId"],
            "items": updated["items"],
            "status": updated["status"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Additional additional order endpoint to update order status
# I was considering not doing this but needed it to write my test file
@app.patch("/orders/{orderId}/status")
def update_order_status(orderId: int, status: str = Body(...)): # We use Body here because we want to pass the status in the body of the request, and the ... means it's required
    try:
        orders_repository.mark_order_status(orderId, status) # This will raise a ValueError if the status is invalid or if the order is not found, which we catch and return as a 400 Bad Request
        order = orders_repository.get_order_by_id(orderId)
        return {"orderId": orderId, "status": order["status"]}
    except ValueError as e: # If the order is not found or if the status is invalid, we catch the ValueError and return a 400 Bad Request with the error message
        raise HTTPException(status_code=400, detail=str(e))