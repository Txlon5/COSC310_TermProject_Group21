from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200


def test_get_restaurant_menu_valid():
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200


def test_get_restaurant_menu_invalid():
    response = client.get("/restaurants/999/menu")
    assert response.status_code == 404


def test_post_menu_valid():
    response = client.post("/menus", json={
        "restaurant_id": 1,
        "name": "Burger",
        "price": 9.99
    })
    assert response.status_code in [200, 201]


def test_post_menu_invalid_restaurant():
    response = client.post("/menus", json={
        "restaurant_id": 999,
        "name": "Fake Burger",
        "price": 9.99
    })
    assert response.status_code == 400