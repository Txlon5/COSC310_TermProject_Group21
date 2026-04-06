import pytest
from fastapi import HTTPException

from app.repositories.restaurants_repository import RestaurantsRepository
from app.schemas.menu import CreateMenuItem
from app.services.menu_service import create_menu_item, fetch_all_menus, fetch_menu_by_restaurant_id,update_menu_item, delete_menu_item
from app.schemas.menu import UpdateMenuItem




RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"


def seed_restaurant():
    repo = RestaurantsRepository()
    repo.save_all([
        {
            "restaurant_id": RESTAURANT_ID,
            "restaurant_name": "Test Pizza",
            "tags": ["pizza"],
            "isOpen": True,
            "opening_time": "09:00",
            "closing_time": "21:00",
            "menuItems": [
                {"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "category": "Food"},
                {"menuItemId": 2, "name": "Cheesey Bread", "price": 15.0, "category": "Food"},
                {"menuItemId": 3, "name": "Canadian Pizza", "price": 23.0, "category": "Food"},
            ]
        }
    ])


def test_fetch_all_menus():
    seed_restaurant()

    result = fetch_all_menus()

    assert len(result) == 1
    assert result[0]["restaurant_id"] == RESTAURANT_ID
    assert len(result[0]["menuItems"]) == 3


def test_fetch_menu_by_restaurant_id():
    seed_restaurant()

    result = fetch_menu_by_restaurant_id(RESTAURANT_ID)

    assert len(result) == 3
    assert result[0].menuItemId == 1


def test_fetch_menu_not_found():
    seed_restaurant()

    with pytest.raises(HTTPException) as exc_info:
        fetch_menu_by_restaurant_id("bad-id")

    assert exc_info.value.status_code == 404


def test_create_menu_item():
    seed_restaurant()

    item = create_menu_item(RESTAURANT_ID,CreateMenuItem(name="Fries", price=5.0, category="Food"))

    assert item.menuItemId == 4
    assert item.name == "Fries"


def test_create_menu_item_invalid_restaurant():
    seed_restaurant()

    with pytest.raises(HTTPException) as exc_info:
        create_menu_item("bad-id",CreateMenuItem(name="Burger", price=12.0, category="Food"))

    assert exc_info.value.status_code == 400
def test_create_menu_item_empty_name():
    seed_restaurant()

    with pytest.raises(HTTPException):
        create_menu_item(RESTAURANT_ID,CreateMenuItem(name="", price=5.0, category="Food"))


def test_create_menu_item_bad_price():
    seed_restaurant()

    with pytest.raises(HTTPException):
        create_menu_item(RESTAURANT_ID,CreateMenuItem(name="Fries", price=0, category="Food"))


def test_update_menu_item_success():
    seed_restaurant()

    updated = update_menu_item(
        RESTAURANT_ID,
        1,
        UpdateMenuItem(name="Updated Pizza", price=12.0, category="Food")
    )

    assert updated["name"] == "Updated Pizza"
    assert updated["price"] == 12.0


def test_update_menu_item_not_found():
    seed_restaurant()

    with pytest.raises(HTTPException):
        update_menu_item(
            RESTAURANT_ID,
            999,
            UpdateMenuItem(name="Fake", price=10.0, category="Food")
        )


def test_update_menu_item_invalid_data():
    seed_restaurant()

    with pytest.raises(HTTPException):
        update_menu_item(RESTAURANT_ID,1,UpdateMenuItem(name="", price=-5, category=""))


def test_delete_menu_item_success():
    seed_restaurant()

    delete_menu_item(RESTAURANT_ID, 1)

    menu = fetch_menu_by_restaurant_id(RESTAURANT_ID)
    ids = [item.menuItemId for item in menu]

    assert 1 not in ids


def test_delete_menu_item_not_found():
    seed_restaurant()

    with pytest.raises(HTTPException):
        delete_menu_item(RESTAURANT_ID, 999)


def test_delete_menu_item_bad_restaurant():
    seed_restaurant()

    with pytest.raises(HTTPException):
        delete_menu_item("bad-id", 1)