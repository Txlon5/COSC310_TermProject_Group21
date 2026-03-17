import pytest
from fastapi import HTTPException
from app.services import menu_service
from app.schemas.menu import MenuCreate, Menu


def test_fetch_all_menus_returns_all_menus(monkeypatch):
    fake_menus = [
        Menu(id=1, restaurant_id=1, name="Burger", price=8.99),
        Menu(id=2, restaurant_id=1, name="Fries", price=3.99),
    ]

    monkeypatch.setattr(menu_service, "get_all_menus", lambda: fake_menus)

    result = menu_service.fetch_all_menus()

    assert result == fake_menus
    assert len(result) == 2


def test_fetch_menu_by_restaurant_id_returns_matching_items(monkeypatch):
    fake_restaurants = [
        {"id": 1, "name": "Burger Place"},
        {"id": 2, "name": "Pizza Spot"},
    ]

    fake_menus = [
        Menu(id=1, restaurant_id=1, name="Burger", price=8.99),
        Menu(id=2, restaurant_id=1, name="Fries", price=3.99),
        Menu(id=3, restaurant_id=2, name="Pizza", price=12.99),
    ]

    monkeypatch.setattr(menu_service, "get_all_restaurants", lambda: fake_restaurants)
    monkeypatch.setattr(menu_service, "get_all_menus", lambda: fake_menus)

    result = menu_service.fetch_menu_by_restaurant_id(1)

    assert len(result) == 2
    assert all(item.restaurant_id == 1 for item in result)


def test_fetch_menu_by_restaurant_id_raises_404_for_missing_restaurant(monkeypatch):
    fake_restaurants = [
        {"id": 1, "name": "Burger Place"},
        {"id": 2, "name": "Pizza Spot"},
    ]

    fake_menus = []

    monkeypatch.setattr(menu_service, "get_all_restaurants", lambda: fake_restaurants)
    monkeypatch.setattr(menu_service, "get_all_menus", lambda: fake_menus)

    with pytest.raises(HTTPException) as exc:
        menu_service.fetch_menu_by_restaurant_id(999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Restaurant not found"


def test_create_menu_returns_added_menu_for_valid_restaurant(monkeypatch):
    fake_restaurants = [
        {"id": 1, "name": "Burger Place"},
        {"id": 2, "name": "Pizza Spot"},
    ]

    new_menu_data = MenuCreate(
        restaurant_id=1,
        name="Onion Rings",
        price=5.99
    )

    expected_menu = Menu(
        id=6,
        restaurant_id=1,
        name="Onion Rings",
        price=5.99
    )

    monkeypatch.setattr(menu_service, "get_all_restaurants", lambda: fake_restaurants)
    monkeypatch.setattr(menu_service, "add_menu", lambda menu_data: expected_menu)

    result = menu_service.create_menu(new_menu_data)

    assert result == expected_menu
    assert result.restaurant_id == 1
    assert result.name == "Onion Rings"


def test_create_menu_raises_400_for_invalid_restaurant(monkeypatch):
    fake_restaurants = [
        {"id": 1, "name": "Burger Place"},
        {"id": 2, "name": "Pizza Spot"},
    ]

    new_menu_data = MenuCreate(
        restaurant_id=999,
        name="Fake Burger",
        price=10.99
    )

    monkeypatch.setattr(menu_service, "get_all_restaurants", lambda: fake_restaurants)

    with pytest.raises(HTTPException) as exc:
        menu_service.create_menu(new_menu_data)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Restaurant does not exist"