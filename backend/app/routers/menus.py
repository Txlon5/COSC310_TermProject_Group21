from fastapi import APIRouter
from app.services.menu_service import fetch_all_menus, fetch_menu_by_restaurant_id

router = APIRouter()

@router.get("/menus")
def get_menus():
    return fetch_all_menus()

@router.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: int):
    return fetch_menu_by_restaurant_id(restaurant_id)