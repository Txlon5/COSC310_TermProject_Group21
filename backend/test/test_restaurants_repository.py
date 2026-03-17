# Import the repository class we want to test
from app.repositories.restaurants_repository import RestaurantsRepository


# Test that the repository returns a list of restaurants
def test_repository_returns_restaurants():

    repo = RestaurantsRepository() # Create an instance of the repository

    data = repo.get_all() # Call the method we are testing

    assert isinstance(data, list) # Verify the returned value is a list

    assert len(data) > 0 # Ensure the list is not empty

    assert "restaurant_id" in data[0] # Verify the structure matches our class diagram