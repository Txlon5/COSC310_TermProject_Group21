from fastapi import APIRouter, status
from app.schemas.menu import MenuItem, CreateMenuItem, UpdateMenuItem
from app.services.menu_service import fetch_menu_by_restaurant_id, fetch_all_menus, create_menu_item, update_menu_item, delete_menu_item


router = APIRouter(tags=["Menu"])

@router.get("/menus")
def get_menus():
    return fetch_all_menus()

@router.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
def get_restaurant_menu(restaurant_id: str):
    return fetch_menu_by_restaurant_id(restaurant_id)

@router.post("/restaurants/{restaurant_id}/menu-item/add", response_model=MenuItem)
def create_restaurant_menu_item(restaurant_id: str, payload: CreateMenuItem):
    return create_menu_item(restaurant_id, payload)

@router.put("/restaurants/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_restaurant_menu_item(restaurant_id: str, menu_item_id: int, payload: UpdateMenuItem):
    return update_menu_item(restaurant_id, menu_item_id, payload)


@router.delete("/restaurants/{restaurant_id}/menu/{menu_item_id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_restaurant_menu_item(restaurant_id: str, menu_item_id: int):
    delete_menu_item(restaurant_id, menu_item_id)