# Import the repository class
# The service will depend on the repository to retrieve data
from app.repositories.restaurants_repository import RestaurantsRepository


# This class represents the Business Logic Layer for restaurants
class RestaurantsService:

    def __init__(self, repo):
        # Store the repository instance inside the service
        # This allows the service to call repository methods
        self.repo = repo

    # Public method to get all restaurants
    # This is what the API layer will call
    def get_restaurants(self):

        restaurants = self.repo.get_all() # Call the repository to retrieve raw data

        # For now, we return it directly, until filtering and all is added
        return restaurants