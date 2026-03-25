from fastapi.testclient import TestClient
from app.main import app
from app.repositories.restaurants_repository import RestaurantsRepository

client = TestClient(app)

RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"


def seed_restaurant():
    repo = RestaurantsRepository()
    repo.save_all([
        {
            "restaurant_id": RESTAURANT_ID,
            "restaurant_name": "Test Pizza",
            "tags": ["pizza"],
            "isOpen": True,
            "menuItems": [
                {
                    "menuItemId": 1,
                    "name": "Pizza",
                    "price": 10.0,
                    "category": "Food"
                },
                {
                    "menuItemId": 2,
                    "name": "Veggie Pizza",
                    "price": 18.0,
                    "category": "Food"
                },
                {
                    "menuItemId": 3,
                    "name": "Canadian Pizza",
                    "price": 23.0,
                    "category": "Food"
                }
            ]
        }
    ])


def test_get_all_menus():
    seed_restaurant()

    response = client.get("/menus")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["restaurant_id"] == RESTAURANT_ID
    assert len(data[0]["menuItems"]) == 3


def test_get_restaurant_menu():
    seed_restaurant()

    response = client.get(f"/restaurants/{RESTAURANT_ID}/menu")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Pizza"
    assert data[1]["name"] == "Veggie Pizza"
    assert data[2]["name"] == "Canadian Pizza"


def test_create_menu_item():
    seed_restaurant()

    payload = {
        "name": "Milkshake",
        "price": 6.25,
        "category": "Drink"
    }

    response = client.post(f"/restaurants/{RESTAURANT_ID}/menu-item/add", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["menuItemId"] == 4
    assert data["name"] == "Milkshake"
    assert data["price"] == 6.25
    assert data["category"] == "Drink"


def test_create_bad_menu_item():
    seed_restaurant()

    payload = {
        "name": "",
        "price": -2,
        "category": ""
    }

    response = client.post(f"/restaurants/{RESTAURANT_ID}/menu-item/add", json=payload)
    assert response.status_code in [400, 422]


def test_update_menu_item():
    seed_restaurant()

    payload = {
        "name": "Cheese Pizza",
        "price": 12.0,
        "category": "Food"
    }

    response = client.put(f"/restaurants/{RESTAURANT_ID}/menu/1", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["menuItemId"] == 1
    assert data["name"] == "Cheese Pizza"
    assert data["price"] == 12.0
    assert data["category"] == "Food"


def test_update_missing_menu_item():
    seed_restaurant()

    payload = {
        "name": "Fake Pizza",
        "price": 9.0,
        "category": "Food"
    }

    response = client.put(f"/restaurants/{RESTAURANT_ID}/menu/999", json=payload)
    assert response.status_code == 404


def test_delete_menu_item():
    seed_restaurant()

    response = client.delete(f"/restaurants/{RESTAURANT_ID}/menu/2")
    assert response.status_code == 204


def test_deleted_item_is_removed():
    seed_restaurant()

    response = client.delete(f"/restaurants/{RESTAURANT_ID}/menu/2")
    assert response.status_code == 204

    response = client.get(f"/restaurants/{RESTAURANT_ID}/menu")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    ids = [item["menuItemId"] for item in data]
    assert 2 not in ids


def test_menu_item_id_increases():
    seed_restaurant()

    payload1 = {
        "name": "Fries",
        "price": 5.0,
        "category": "Food"
    }

    payload2 = {
        "name": "Juice",
        "price": 3.0,
        "category": "Drink"
    }

    response1 = client.post(f"/restaurants/{RESTAURANT_ID}/menu-item/add", json=payload1)
    response2 = client.post(f"/restaurants/{RESTAURANT_ID}/menu-item/add", json=payload2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    assert data1["menuItemId"] == 4
    assert data2["menuItemId"] == 5