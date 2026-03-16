from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.restaurants import RestaurantOut
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService
from app.data.restaurants_data import RESTAURANTS

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Create repository instance
restaurants_repository = RestaurantsRepository()

# Inject repository into the service
restaurants_service = RestaurantsService(restaurants_repository)

@router.get("", response_model=List[RestaurantOut])
def get_restaurants(
    q: Optional[str] = Query(default=None),
    restaurantId: Optional[int] = Query(default=None, ge=1),
    isOpen: Optional[bool] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    page: Optional[int] = Query(default=None, ge=1),
    pageSize: Optional[int] = Query(default=None, ge=1),
):
    try:
        if q is not None and str(q).strip() == "":
            raise HTTPException(status_code=400, detail="q cannot be empty")

        if q is None and restaurantId is None and isOpen is None and tag is None and page is None and pageSize is None:
            return restaurants_service.get_restaurants()

        return restaurants_service.search_restaurants(
            q=q,
            restaurant_id=restaurantId,
            is_open=isOpen,
            tag=tag,
            page=page,
            page_size=pageSize,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/debug")
def debug_data():
    return RESTAURANTS
