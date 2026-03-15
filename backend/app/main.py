from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional

from app.routers.orders import router as orders_router
from app.routes.order import router as order_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

from app.routers.notifications import router as notifications_router

# RESTAURANT STUFF - I am unsure if we will put all imports and such in main?
from app.data.restaurants_data import RESTAURANTS
from app.schemas.restaurants import RestaurantOut
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService
# END Restaurant imports

app = FastAPI()
app.include_router(orders_router)   #Include the orders router to make the order creation endpoint available.
app.include_router(users_router)    #Include the users router to make user management endpoints available.
app.include_router(auth_router)     #Include the auth router to make authentication endpoints available.
app.include_router(notifications_router, tags = ["Notifications"])    #Include the notifications router to make the notifications retrieval endpoint available.

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
        if q is not None and str(q).strip() == "":
            raise HTTPException(status_code=400, detail="q cannot be empty")

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