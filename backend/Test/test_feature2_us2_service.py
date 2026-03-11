import pytest
from fastapi import HTTPException
from app.schemas.menu import MenuCreate
from app.schemas.restaurant import RestaurantCreate
from app.services.menu_service import create_menu, create_restaurant


def test_create_restaurant_valid():
    restaurant = create_restaurant(RestaurantCreate(name="Pasta Place"))
    assert restaurant.name == "Pasta Place"


def test_create_menu_valid():
    menu = create_menu(
        MenuCreate(
            restaurant_id=1,
            name="Fish Burger",
            price=11.99
        )
    )
    assert menu.restaurant_id == 1
    assert menu.name == "Fish Burger"
    assert menu.price == 11.99


def test_create_menu_invalid_restaurant():
    with pytest.raises(HTTPException) as exc_info:
        create_menu(
            MenuCreate(
                restaurant_id=999,
                name="Bad Menu",
                price=7.99
            )
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Restaurant does not exist"