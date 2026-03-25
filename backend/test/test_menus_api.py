import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
RESTAURANT_ID = "facf5d81-4bd9-4003-9c08-1b98471b2c34"

# Test Setup - Setup Mock data/function calls for Fetching/Saving Restaurants
@pytest.fixture(autouse=True)
def setup_fake_repo():
    # Mock Restaurant Database
    fake_db = [
        {
            "restaurant_id": RESTAURANT_ID,
            "restaurant_name": "Pizza Place",
            "tags": ["Italian", "Pizza"],
            "isOpen": True,
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


def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200


def test_get_restaurant_menu_valid():
    restaurant_id = RESTAURANT_ID
    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 200

def test_get_restaurant_menu_invalid():
    restaurant_id = "999"
    response = client.get(f"/restaurants/{restaurant_id}/menu")
    assert response.status_code == 404


def test_post_menu_valid():
    restaurant_id = RESTAURANT_ID
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