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

    assert "restaurant_id" in data[0] # Verify structure matches class diagram
    
    
class FakeRestaurantsRepository: # As mentioned in the service file, this might change according to what we do with the CSV file
# For now, we're going to make a class with a specific structure
    def get_all(self):
        return [
            {
                "restaurant_id": 1,
                "restaurant_name": "Pizza Place",
                "tags": ["Italian", "Pizza"],
                "isOpen": True,
                "menuItems": [
                    {"menuItemId": 1, "name": "Pepperoni Pizza", "price": 15.0, "category": "Pizza"},
                    {"menuItemId": 2, "name": "Veggie Pizza", "price": 13.0, "category": "Pizza"},
                ],
            },
            {
                "restaurant_id": 2,
                "restaurant_name": "Burger House",
                "tags": ["Fast Food", "Burgers"],
                "isOpen": False,
                "menuItems": [
                    {"menuItemId": 1, "name": "Cheeseburger", "price": 10.0, "category": "Burger"},
                ],
            },
        ]

# Test that the service correctly returns restaurant data
def test_service_returns_restaurants():

    repo = RestaurantsRepository() # Create repository instance

    service = RestaurantsService(repo) # Putting repository into service

    data = service.get_restaurants() # Calling the service method

    assert isinstance(data, list) # Ensure the result is a list

    assert len(data) > 0 # Ensure the list is not empty

    assert "restaurant_id" in data[0] # Verify structure matches class diagram
    
    
def test_filter_by_restaurant_id():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    if not all_data:
        pytest.skip("No restaurant data available from CSV.")
    # Pick a valid restaurant_id from CSV
    valid_id = all_data[0]["restaurant_id"]
    data = service.search_restaurants(restaurant_id=valid_id)
    assert len(data) >= 1
    assert all(d["restaurant_id"] == valid_id for d in data)

def test_filter_by_is_open():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    data = service.search_restaurants(is_open=True)
    assert isinstance(data, list)
    # All returned restaurants should be open
    assert all(d["isOpen"] is True for d in data)


def test_filter_by_tag():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    if not all_data:
        pytest.skip("No restaurant data available from CSV.")
    # Pick a valid tag from CSV
    valid_tag = all_data[0]["tags"][0] if all_data[0]["tags"] else None
    if not valid_tag:
        pytest.skip("No tag data available from CSV.")
    data = service.search_restaurants(tag=valid_tag)
    assert len(data) >= 1
    assert any(valid_tag.lower() in [t.lower() for t in d["tags"]] for d in data)


def test_invalid_empty_tag_rejected():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    with pytest.raises(ValueError):
        service.search_restaurants(tag="  ")

def test_search_q_matches_restaurant_name():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    if not all_data:
        pytest.skip("No restaurant data available from CSV.")
    valid_name = all_data[0]["restaurant_name"]
    data = service.search_restaurants(q=valid_name)
    assert len(data) >= 1
    assert any(valid_name.lower() in d["restaurant_name"].lower() for d in data)
    
def test_search_q_matches_menu_item_name():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    if not all_data:
        pytest.skip("No restaurant data available from CSV.")
    menu_items = all_data[0]["menuItems"]
    if not menu_items:
        pytest.skip("No menu items available from CSV.")
    valid_item = menu_items[0]["name"]
    data = service.search_restaurants(q=valid_item)
    assert len(data) >= 1
    assert any(valid_item.lower() in [it["name"].lower() for it in d["menuItems"]] for d in data)


def test_empty_q_returns_empty_list():
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    result = service.search_restaurants(q="")
    assert result == []
        
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
    repo = RestaurantsRepository()
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    if not all_data:
        pytest.skip("No restaurant data available from CSV.")
    data = service.search_restaurants(page=1, page_size=1)
    assert len(data) == 1

def test_search_with_pagination_page2_no_duplicates():
    repo = RestaurantsRepository()
    repo._restaurants = None  # Force reload from CSV
    service = RestaurantsService(repo)
    all_data = service.get_restaurants()
    assert isinstance(all_data, list)
    assert len(all_data) >= 2, "Need at least 2 restaurants for pagination test."
    page1 = service.search_restaurants(page=1, page_size=1)
    page2 = service.search_restaurants(page=2, page_size=1)
    assert len(page1) == 1, "Page 1 should return one restaurant."
    assert len(page2) == 1, "Page 2 should return one restaurant."
    assert page1[0]["restaurant_id"] != page2[0]["restaurant_id"], "Page 1 and Page 2 should return different restaurants."

def get_all(self):
    return [
        {
            "restaurant_id": 1,
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