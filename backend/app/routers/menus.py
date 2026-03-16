from fastapi import APIRouter
from app.schemas.menu import MenuCreate
from app.schemas.restaurant import RestaurantCreate
from app.services.menu_service import ( fetch_all_menus, fetch_all_restaurants, fetch_menu_by_restaurant_id, create_menu, create_restaurant)

router = APIRouter(tags=["Menu"])


@router.get("/menus")
def get_menus():
    return fetch_all_menus()


@router.post("/menus")
def add_new_menu(menu_data: MenuCreate):
    return create_menu(menu_data)


@router.get("/restaurants")
def get_restaurants():
    return fetch_all_restaurants()


@router.post("/restaurants")
def add_new_restaurant(restaurant_data: RestaurantCreate):
    return create_restaurant(restaurant_data)


@router.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: int):
    return fetch_menu_by_restaurant_id(restaurant_id)