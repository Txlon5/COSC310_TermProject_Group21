from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_restaurants():
    response = client.get("/restaurants")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "name" in data[0]


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "restaurant_id" in data[0]
    assert "name" in data[0]
    assert "price" in data[0]


def test_get_restaurant_menu_valid():
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    for item in data:
        assert item["restaurant_id"] == 1


def test_get_restaurant_menu_invalid():
    response = client.get("/restaurants/99/menu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"