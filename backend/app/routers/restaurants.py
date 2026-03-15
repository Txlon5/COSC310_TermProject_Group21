from fastapi import APIRouter, status
from typing import List
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.restaurants_service import RestaurantsService
from app.repositories.restaurants_repository import RestaurantsRepository

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

repo = RestaurantsRepository()
service = RestaurantsService(repo)


@router.get("", response_model=List[Restaurant])
def get_restaurants():
    return service.list_restaurants()


@router.post("", response_model=Restaurant, status_code=201)
def post_restaurant(payload: RestaurantCreate):
    return service.create_restaurant(payload)


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return service.get_restaurant_by_id(restaurant_id)


@router.put("/{restaurant_id}", response_model=Restaurant)
def put_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return service.update_restaurant(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_restaurant(restaurant_id: str):
    service.delete_restaurant(restaurant_id)
    return None