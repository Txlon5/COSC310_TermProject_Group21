from fastapi import APIRouter
from app.schemas.menu import MenuCreate, MenuItem, CreateMenuItem
from app.services.menu_service import fetch_menu_by_restaurant_id, fetch_all_menus, create_menu_item

from app.repositories.restaurants_repository import RestaurantsRepository

router = APIRouter(tags=["Menu"])

@router.get("/menus")
def get_menus():
    return fetch_all_menus()

@router.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: str):
    return fetch_menu_by_restaurant_id(restaurant_id)

@router.post("/restaurants/{restaurant_id}/menu-item/add", response_model=MenuItem)
def create_restaurant_menu_item(restaurant_id: str, payload: CreateMenuItem):
    return create_menu_item(restaurant_id, payload)