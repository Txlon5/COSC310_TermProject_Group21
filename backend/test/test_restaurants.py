# This file is here to test the instance of data, mock data for now, in restuarants

from app.data.restaurants_data import RESTAURANTS # Grabbing the RESTAURTANTS class

# Test 1: Make sure the dataset exists and is a list
def test_restaurants_data_exists():
    
    assert isinstance(RESTAURANTS, list) # Check that RESTAURANTS is a list object

    assert len(RESTAURANTS) > 0 # Make sure that it's not empty

# Test 2: Validate structure of one restaurant entry
def test_restaurant_structure():

    r = RESTAURANTS[0] # Take the first restaurant from the list

    # If we're going according to our class diagram, these names must be set
    assert "restaurantId" in r      # Restaurant must have restaurantId
    assert "name" in r              # Restaurant must have name
    assert "tags" in r              # Restaurant must have tags
    assert "isOpen" in r            # Restaurant must have isOpen status
    assert "menuItems" in r         # Restaurant must contain menuItems list

    assert isinstance(r["menuItems"], list) # Ensure menuItems is actually a list