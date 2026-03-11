import pytest
from fastapi import HTTPException
from app.services.menu_service import ( fetch_all_menus, fetch_all_restaurants, fetch_menu_by_restaurant_id)


def test_fetch_all_restaurants():
    restaurants = fetch_all_restaurants()
    assert isinstance(restaurants, list)
    assert len(restaurants) >= 1


def test_fetch_all_menus():
    menus = fetch_all_menus()
    assert isinstance(menus, list)
    assert len(menus) >= 1


def test_fetch_menu_by_restaurant_id_valid():
    menu_items = fetch_menu_by_restaurant_id(1)
    assert isinstance(menu_items, list)
    assert len(menu_items) >= 1

    for item in menu_items:
        assert item.restaurant_id == 1


def test_fetch_menu_by_restaurant_id_invalid():
    with pytest.raises(HTTPException) as exc_info:
        fetch_menu_by_restaurant_id(99)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Restaurant not found"