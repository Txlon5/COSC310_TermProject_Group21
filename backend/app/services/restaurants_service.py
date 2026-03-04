import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.repositories.restaurants_repo import load_all, save_all


def list_restaurants() -> List[Restaurant]:
    return [Restaurant(**it) for it in load_all()]

def create_restaurant(payload: RestaurantCreate) -> Restaurant:
    restaurants = load_all()
    new_id = str(uuid.uuid4())
    if any(it.get("id") == new_id for it in restaurants):  # extremely unlikely, but consistent check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_restaurant = Restaurant(id=new_id, name=payload.name.strip(), category=payload.category.strip(), tags=payload.tags)
    restaurants.append(new_restaurant.dict())
    save_all(restaurants)
    return new_restaurant

def get_restaurant_by_id(restaurant_id: str) -> Restaurant:
    restaurants = load_all()
    for it in restaurants:
        if it.get("id") == restaurant_id:
            return Restaurant(**it)
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def update_restaurant(restaurant_id: str, payload: RestaurantUpdate) -> Restaurant:
    restaurants = load_all()
    for idx, it in enumerate(restaurants):
        if it.get("id") == restaurant_id:
            updated = Restaurant(
                id=restaurant_id,
                name=payload.name.strip(),
                category=payload.category.strip(),
                tags=payload.tags,
            )
            restaurants[idx] = updated.dict()
            save_all(restaurants)
            return updated
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def delete_restaurant(restaurant_id: str) -> None:
    restaurants = load_all()
    new_restaurants = [it for it in restaurants if it.get("id") != restaurant_id]
    if len(new_restaurants) == len(restaurants):
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")
    save_all(new_restaurants)