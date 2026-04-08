import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test Setup - Setup Mock data/function calls for Fetching/Saving Restaurants
@pytest.fixture(autouse=True)
def setup_fake_repo():
    # Mock Restaurant Database
    fake_db = [
        {
            "restaurant_id": "facf5d81-4bd9-4003-9c08-1b98471b2c34",
            "restaurant_name": "Pizza Place",
            "tags": ["Italian", "Pizza"],
            "isOpen": True,
            "opening_time": "09:00",
            "closing_time": "21:00",
            "menuItems": []
        }
    ]

    # Return mock list
    def mock_load():
        return fake_db.copy() 
    
    # Save mock list
    def mock_save(data):
        fake_db.clear()
        fake_db.extend(data)

    # Apply mock functions
    with patch("app.repositories.restaurants_repository.RestaurantsRepository.load_all", side_effect=mock_load), \
         patch("app.repositories.restaurants_repository.RestaurantsRepository.save_all", side_effect=mock_save):
        yield


def test_get_restaurants():
    response = client.get("/restaurants")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_restaurant():
    new_restaurant = {
        "restaurant_name": "Test Pizza",
        "tags": ["pizza"],
        "isOpen": True,
        "opening_time": "10:00",
        "closing_time": "19:00",
    }

    response = client.post("/restaurants", json=new_restaurant)

    assert response.status_code == 201 # Check that restaurant created successfully
    data = response.json()

    assert data["restaurant_name"] == "Test Pizza"
    assert "restaurant_id" in data


def test_get_restaurant_by_id():
    new_restaurant = {
        "restaurant_name": "Test Burger",
        "category": "Fast Food",
        "tags": ["burger"],
        "isOpen": True,
        "opening_time": "08:00",
        "closing_time": "21:00",
    }

    create_response = client.post("/restaurants", json=new_restaurant)
    assert create_response.status_code == 201 # Check that restaurant created successfully
    restaurant_id = create_response.json()["restaurant_id"]

    response = client.get(f"/restaurants/{restaurant_id}")

    assert response.status_code == 200
    assert response.json()["restaurant_id"] == restaurant_id


def test_delete_restaurant():
    new_restaurant = {
        "restaurant_name": "Delete Me",
        "category": "Test",
        "tags": [],
        "isOpen": False,
        "opening_time": "07:00",
        "closing_time": "19:00",
    }

    create_response = client.post("/restaurants", json=new_restaurant)
    assert create_response.status_code == 201 # Check that restaurant created successfully
    restaurant_id = create_response.json()["restaurant_id"]

    delete_response = client.delete(f"/restaurants/{restaurant_id}")

    assert delete_response.status_code == 204