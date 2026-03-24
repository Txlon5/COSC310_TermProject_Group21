from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200


def test_get_restaurant_menu_valid():
    restaurant_id = "6fc1000b-6494-4f0e-b8a1-4888f669f975"
    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 200

def test_get_restaurant_menu_invalid():
    restaurant_id = "999"
    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 404


def test_post_menu_valid():
    restaurant_id = "6fc1000b-6494-4f0e-b8a1-4888f669f975"
    response = client.post(f"/restaurants/{restaurant_id}/menu-item/add", json={
        "name": "Burger",
        "price": 9.99,
        "category": "Mains"
    })
    assert response.status_code == 200

def test_post_menu_invalid_restaurant():
    restaurant_id = "999"
    response = client.post(f"/restaurants/{restaurant_id}/menu-item/add", json={
        "name": "Fake Burger",
        "price": 9.99,
        "category": "Mains"
    })
    assert response.status_code == 400