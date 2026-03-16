# Import service and repository
from app.services.restaurants_service import RestaurantsService
from app.repositories.restaurants_repository import RestaurantsRepository
import pytest # Will be helpful to test raising errors
from fastapi import HTTPException

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
    data = service.search_restaurants(is_open=True) # See if it's open, so we should get the pizza place but not the burger house
    assert len(data) == 1
    assert data[0]["restaurantId"] == 1


def test_filter_by_tag():
    service = RestaurantsService(FakeRestaurantsRepository())
    data = service.search_restaurants(tag="pizza") # Search by pizza tag, should return the pizza place but not the burger house
    assert len(data) == 1
    assert data[0]["restaurantId"] == 1


def test_invalid_empty_tag_rejected():
    service = RestaurantsService(FakeRestaurantsRepository())
    with pytest.raises(ValueError): # Check if we get an error when we put an invalid tag, which in this case is just an empty string with whitespace
        service.search_restaurants(tag="  ")    

def test_search_q_matches_restaurant_name():
    service = RestaurantsService(FakeRestaurantsRepository())
    data = service.search_restaurants(q="burger") # Search by burger,
    assert len(data) == 1
    assert data[0]["restaurantId"] == 2
    
def test_search_q_matches_menu_item_name():
    service = RestaurantsService(FakeRestaurantsRepository())
    data = service.search_restaurants(q="pepperoni") # Now try looking for a menu item, should return the pizza place because of the pepperoni pizza
    assert len(data) == 1
    assert data[0]["restaurantId"] == 1


def test_empty_q_returns_empty_list():
    service = RestaurantsService(FakeRestaurantsRepository())
    result = service.search_restaurants(q="")
    assert result == []  # Expecting an empty list when q is an empty string, this works for Feat3-US1 :) I should've implemented it sooner
        
"""SR3 PAGINATION TESTS"""

def test_paginate_limits_by_page_size():
    service = RestaurantsService(FakeRestaurantsRepository())
    items = list(range(1, 11))  # 1...10
    page1 = service.paginate(items, page=1, page_size=3)
    assert page1 == [1, 2, 3] # Based on the page size and what's in items, we should get 1, 2, and 3 for page 1

def test_paginate_page2_no_duplicates():
    service = RestaurantsService(FakeRestaurantsRepository())
    items = list(range(1, 11))
    page1 = service.paginate(items, page=1, page_size=3)
    page2 = service.paginate(items, page=2, page_size=3)
    assert page2 == [4, 5, 6] # Page 2 must be 4, 5 and 6
    assert set(page1).isdisjoint(set(page2)) # This is the important part, we want to make sure there are no duplicates

def test_paginate_last_page_partial():
    service = RestaurantsService(FakeRestaurantsRepository())
    items = list(range(1, 11))
    page4 = service.paginate(items, page=4, page_size=3)
    assert page4 == [10] # Final page should just have the last item, which is 10

def test_paginate_invalid_page_rejected():
    service = RestaurantsService(FakeRestaurantsRepository())
    with pytest.raises(ValueError):
        service.paginate([1, 2, 3], page=0, page_size=2) # Page number less than 1 should raise an error

def test_paginate_invalid_page_size_rejected():
    service = RestaurantsService(FakeRestaurantsRepository())
    with pytest.raises(ValueError):
        service.paginate([1, 2, 3], page=1, page_size=0) # Page size less than 1 should raise an error
        
def test_search_with_pagination_limits_results():
    service = RestaurantsService(FakeRestaurantsRepository())
    # Fake repo has 2 restaurants; page_size=1 should return only 1
    data = service.search_restaurants(page=1, page_size=1)
    assert len(data) == 1

def test_search_with_pagination_page2_no_duplicates():
    service = RestaurantsService(FakeRestaurantsRepository())
    page1 = service.search_restaurants(page=1, page_size=1)
    page2 = service.search_restaurants(page=2, page_size=1)
    assert page1[0]["restaurantId"] != page2[0]["restaurantId"] # Just have to make sure the first element of each page is different, since we only have one item per page, this ensures no duplicates across pages

def get_all(self):
    return [
        {
            "restaurantId": 1,
            "name": "Pizza Place",
            "category": "Italian",
            "tags": ["pizza"],
            "isOpen": True,
            "menuItems": []
        }
    ]

def save_all(self, restaurants):
    self.restaurants = restaurants


def test_get_restaurant_by_id_not_found():
    service = RestaurantsService(FakeRestaurantsRepository())

    with pytest.raises(HTTPException) as exc:
        service.get_restaurant_by_id("999")

    assert exc.value.status_code == 404


def test_update_restaurant_not_found():
    service = RestaurantsService(FakeRestaurantsRepository())

    class Payload:
        name = "Updated"
        category = "Test"
        tags = []

    with pytest.raises(HTTPException) as exc:
        service.update_restaurant("999", Payload())

    assert exc.value.status_code == 404


def test_delete_restaurant_not_found():
    service = RestaurantsService(FakeRestaurantsRepository())

    with pytest.raises(HTTPException) as exc:
        service.delete_restaurant("999")

    assert exc.value.status_code == 404