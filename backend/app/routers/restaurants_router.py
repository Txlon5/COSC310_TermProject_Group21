from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.schemas.restaurant import RestaurantOut, RestaurantCreate, RestaurantUpdate, Restaurant
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService


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

@router.post("", response_model=Restaurant, status_code=201)
def post_restaurant(payload: RestaurantCreate):
    return restaurants_service.create_restaurant(payload)


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return restaurants_service.get_restaurant_by_id(restaurant_id)


@router.put("/{restaurant_id}", response_model=Restaurant)
def put_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return restaurants_service.update_restaurant(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_restaurant(restaurant_id: str):
    restaurants_service.delete_restaurant(restaurant_id)
    return None

