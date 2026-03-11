from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_valid_restaurant():
    response = client.post("/restaurants", json={"name": "Taco House"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Taco House"
    assert "id" in data


def test_reject_empty_restaurant_name():
    response = client.post("/restaurants", json={"name": ""})
    assert response.status_code == 422


def test_reject_missing_restaurant_name():
    response = client.post("/restaurants", json={})
    assert response.status_code == 422


def test_create_valid_menu():
    response = client.post(
        "/menus",
        json={
            "restaurant_id": 1,
            "name": "Chicken Burger",
            "price": 9.99
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert data["restaurant_id"] == 1
    assert data["name"] == "Chicken Burger"
    assert data["price"] == 9.99


def test_reject_invalid_restaurant_id_for_menu():
    response = client.post(
        "/menus",
        json={
            "restaurant_id": 99,
            "name": "Bad Item",
            "price": 9.99
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Restaurant does not exist"


def test_reject_empty_menu_name():
    response = client.post(
        "/menus",
        json={
            "restaurant_id": 1,
            "name": "",
            "price": 9.99
        }
    )
    assert response.status_code == 422


def test_reject_negative_menu_price():
    response = client.post(
        "/menus",
        json={
            "restaurant_id": 1,
            "name": "Bad Price",
            "price": -1
        }
    )
    assert response.status_code == 422


def test_reject_missing_menu_field():
    response = client.post(
        "/menus",
        json={
            "restaurant_id": 1,
            "price": 9.99
        }
    )
    assert response.status_code == 422