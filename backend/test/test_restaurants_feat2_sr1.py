from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_restaurants():
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_restaurant():
    new_restaurant = {
        "restaurant_name": "Test Pizza",
        "category": "Italian",
        "tags": ["pizza"]
    }

    response = client.post("/restaurants", json=new_restaurant)

    assert response.status_code == 201
    data = response.json()

    assert data["restaurant_name"] == "Test Pizza"
    assert data["category"] == "Italian"
    assert "restaurant_id" in data


def test_get_restaurant_by_id():
    new_restaurant = {
        "restaurant_name": "Test Burger",
        "category": "Fast Food",
        "tags": ["burger"]
    }

    create_response = client.post("/restaurants", json=new_restaurant)
    restaurant_id = create_response.json()["restaurant_id"]

    response = client.get(f"/restaurants/{restaurant_id}")

    assert response.status_code == 200
    assert response.json()["restaurant_id"] == restaurant_id


def test_delete_restaurant():
    new_restaurant = {
        "restaurant_name": "Delete Me",
        "category": "Test",
        "tags": []
    }

    create_response = client.post("/restaurants", json=new_restaurant)
    restaurant_id = create_response.json()["restaurant_id"]

    delete_response = client.delete(f"/restaurants/{restaurant_id}")

    assert delete_response.status_code == 204