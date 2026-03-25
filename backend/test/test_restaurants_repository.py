from app.repositories.restaurants_repository import RestaurantsRepository


def test_load_all_returns_empty_list_when_file_missing(tmp_path):
    repo = RestaurantsRepository(tmp_path / "missing_restaurants.json")
    data = repo.load_all()

    assert data == []


def test_save_all_and_load_all_work_together(tmp_path):
    path = tmp_path / "restaurants.json"
    repo = RestaurantsRepository(path)

    restaurants = [
        {
            "restaurant_id": "123",
            "restaurant_name": "Round Trip Cafe",
            "tags": ["coffee"],
            "isOpen": True,
            "menuItems": [],
        }
    ]

    repo.save_all(restaurants)

    assert path.exists()
    assert repo.load_all() == restaurants
