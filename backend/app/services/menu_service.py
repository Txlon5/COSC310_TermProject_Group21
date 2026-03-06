from fastapi import HTTPException
from app.repositories.menu_repository import get_all_restaurants, get_all_menus

def fetch_all_menus():
    return get_all_menus()

def fetch_menu_by_restaurant_id(restaurant_id: int):
    restaurants = get_all_restaurants()
    menus = get_all_menus()

    restaurant_exists = False

    for restaurant in restaurants:
        if restaurant["id"] == restaurant_id:
            restaurant_exists = True
            break

    if not restaurant_exists:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    restaurant_menu = []

    for item in menus:
        if item.restaurant_id == restaurant_id:
            restaurant_menu.append(item)

    return restaurant_menu