from fastapi import APIRouter, Query, status
from typing import List, Optional
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantMinimal
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Create repository instance
restaurants_repository = RestaurantsRepository()

# Inject repository into the service
restaurants_service = RestaurantsService(restaurants_repository)

# Get all, search, filter and paginate list of Restaurants
@router.get("", response_model=List[Restaurant])
def get_restaurants(
    q: Optional[str] = Query(default=None),
    restaurant_id: Optional[str] = Query(default=None),
    isOpen: Optional[bool] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    page: Optional[int] = Query(default=None, ge=1),
    pageSize: Optional[int] = Query(default=None, ge=1),
):
    return restaurants_service.get_restaurant_filtered(q, restaurant_id, isOpen, tag, page, pageSize)

# Get minimal detail list of all Restaurants
@router.get("/list", response_model=List[RestaurantMinimal])
def get_restaurant_list():
    return restaurants_service.list_restaurants()

# Get Restaurant by Id
@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant_by_id(restaurant_id: str):
    return restaurants_service.get_restaurant_by_id(restaurant_id)

# Create Restaurant
@router.post("", response_model=Restaurant, status_code=201)
def post_restaurant(payload: RestaurantCreate):
    return restaurants_service.create_restaurant(payload)

# Update Restaurant by Id
@router.put("/{restaurant_id}", response_model=Restaurant)
def put_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return restaurants_service.update_restaurant(restaurant_id, payload)

# Delete Restaurant by Id
@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_restaurant(restaurant_id: str):
    restaurants_service.delete_restaurant(restaurant_id)
    return None

