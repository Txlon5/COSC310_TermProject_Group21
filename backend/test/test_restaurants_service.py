# Import service and repository
from app.services.restaurants_service import RestaurantsService
from app.repositories.restaurants_repository import RestaurantsRepository
import pytest # Will be helpful to test raising errors


# Test that the service correctly returns restaurant data
def test_service_returns_restaurants():

    repo = RestaurantsRepository() # Create repository instance

    service = RestaurantsService(repo) # Putting repository into service

    data = service.get_restaurants() # Calling the service method

    assert isinstance(data, list) # Ensure the result is a list

    assert len(data) > 0 # Ensure the list is not empty

    assert "restaurantId" in data[0] # Verify structure matches class diagram
    
    
class FakeRestaurantsRepository: # As mentioned in the service file, this might change according to what we do with the CSV file
# For now, we're going to make a class with a specific structure
    def get_all(self):
        return [
            {
                "restaurantId": 1,
                "name": "Pizza Place",
                "tags": "Italian, Pizza", # Basically why we're here
                "isOpen": True,
                "menuItems": [
                    {"menuItemId": 1, "name": "Pepperoni Pizza", "price": 15.0, "category": "Pizza"},
                    {"menuItemId": 2, "name": "Veggie Pizza", "price": 13.0, "category": "Pizza"},
                ],
            },
            {
                "restaurantId": 2, # A second restaurant to test for peace of mind
                "name": "Burger House",
                "tags": "Fast Food, Burgers",
                "isOpen": False,
                "menuItems": [
                    {"menuItemId": 1, "name": "Cheeseburger", "price": 10.0, "category": "Burger"},
                ],
            },
        ]


def test_filter_by_restaurant_id():
    service = RestaurantsService(FakeRestaurantsRepository()) # Actually using our fake repository here to test the search functionality, this line is used in every test below for this
    data = service.search_restaurants(restaurant_id=2) # Just testing the search filter for restaurant ID
    assert len(data) == 1
    assert data[0]["restaurantId"] == 2


def test_filter_by_is_open():
    service = RestaurantsService(FakeRestaurantsRepository())
    data = service.search_restaurants(is_open=True)
    assert len(data) == 1
    assert data[0]["restaurantId"] == 1


def test_filter_by_tag():
    service = RestaurantsService(FakeRestaurantsRepository())
    data = service.search_restaurants(tag="pizza")
    assert len(data) == 1
    assert data[0]["restaurantId"] == 1


def test_invalid_empty_tag_rejected():
    service = RestaurantsService(FakeRestaurantsRepository())
    with pytest.raises(ValueError):
        service.search_restaurants(tag="  ")    