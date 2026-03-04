from fastapi import APIRouter, status
from typing import List
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.services.restaurants_service import list_restaurants, create_restaurant,get_restaurant_by_id, delete_restaurant, update_restaurant

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("", response_model=List[Restaurant])
def get_restaurants():
    return list_restaurants()

#simple post the payload (is the body of the request)
@router.post("", response_model=Restaurant, status_code=201)
def post_restaurant(payload: RestaurantCreate):
    return create_restaurant(payload)

#from services.restaurants_service import list_restaurants, create_restaurants, get_restaurant_by_id

@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return get_restaurant_by_id(restaurant_id)

## We use put here because we are not creating an entirely new item, ie. we keep id the same
@router.put("/{restaurant_id}", response_model=Restaurant)
def put_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return update_restaurant(restaurant_id, payload)


## we put the status there becuase in a delete, we wont have a return so it indicates it happened succesfully
@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_restaurant(restaurant_id: str):
    delete_restaurant(restaurant_id)
    return None