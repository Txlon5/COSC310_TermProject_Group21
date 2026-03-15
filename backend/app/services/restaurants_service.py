import uuid  # Used to generate a unique ID for newly created restaurants
from fastapi import HTTPException  # Used to raise API-friendly errors
from app.repositories.restaurants_repository import RestaurantsRepository  # Repository layer for restaurant data


"""
FULL DISCLAIMER
I need to have a chat with the team about how we will do tags.
As of right now, everyone is busy, but I have to continue working regardless.
So for now, SR2 will start like SR1, not using the CSV file, but working with mock data (for now)
"""


# This class represents the Business Logic Layer for restaurants.
# The router talks to this service, and this service talks to the repository.
class RestaurantsService:
    def __init__(self, repo: RestaurantsRepository):
        # Store the repository instance inside the service
        # This allows the service to call repository methods
        self.repo = repo

    def _to_schema_restaurant(self, r):
        return {
            "id": str(r.get("restaurantId")),
            "name": r.get("name", ""),
            "category": r.get("category", "Unknown"),
            "tags": r.get("tags", []),
        }

    # Public method to get all restaurants
    # This is what the API layer will call
    def list_restaurants(self):
        restaurants = self.repo.get_all()
        return [self._to_schema_restaurant(r) for r in restaurants]
    def get_restaurants(self):
        return self.list_restaurants()
    # Creates a new restaurant and appends it to the current restaurant list
    def create_restaurant(self, payload):
        restaurants = self.repo.get_all()

        new_restaurant = {
            "restaurantId": str(uuid.uuid4()),
            "name": payload.name.strip(),
            "category": payload.category.strip(),
            "tags": payload.tags if payload.tags is not None else [],
            "isOpen": True,
            "menuItems": []
        }

        restaurants.append(new_restaurant)

        if hasattr(self.repo, "save_all"):
            self.repo.save_all(restaurants)

        return self._to_schema_restaurant(new_restaurant)

    # Returns a single restaurant by its restaurantId
    def get_restaurant_by_id(self, restaurant_id: str):
        restaurants = self.repo.get_all()

        for r in restaurants:
            if str(r.get("restaurantId")) == str(restaurant_id) or str(r.get("id")) == str(restaurant_id):
                return self._to_schema_restaurant(r)

        raise HTTPException(status_code=404,detail=f"Restaurant '{restaurant_id}' not found")

    # Updates an existing restaurant by ID
     def update_restaurant(self, restaurant_id: str, payload):
        restaurants = self.repo.get_all()

        for r in restaurants:
            if str(r.get("restaurantId")) == str(restaurant_id) or str(r.get("id")) == str(restaurant_id):
                r["name"] = payload.name.strip()
                r["category"] = payload.category.strip()

                if payload.tags is not None:
                    r["tags"] = payload.tags

                if hasattr(self.repo, "save_all"):
                    self.repo.save_all(restaurants)

                return self._to_schema_restaurant(r)

        raise HTTPException(status_code=404,detail=f"Restaurant '{restaurant_id}' not found")

    # Deletes a restaurant by ID
     def delete_restaurant(self, restaurant_id: str):
        restaurants = self.repo.get_all()

        for i, r in enumerate(restaurants):
            if str(r.get("restaurantId")) == str(restaurant_id) or str(r.get("id")) == str(restaurant_id):
                restaurants.pop(i)

                if hasattr(self.repo, "save_all"):
                    self.repo.save_all(restaurants)

                return

        raise HTTPException(status_code=404,detail=f"Restaurant '{restaurant_id}' not found")

    # THE BELOW FUNCTION IS FOR SR3 - PAGINATION
    # Users can put in a page count and how many items they want per page
    def paginate(self, items, page, page_size):
        # If no pagination parameters are given, just return all items
        if page is None or page_size is None:
            return items

        # Validate page number
        if page < 1:
            raise ValueError("page must be >= 1")

        # Validate page size
        if page_size < 1:
            raise ValueError("pageSize must be >= 1")

        # Calculate slice boundaries
        start = (page - 1) * page_size
        end = start + page_size

        # Return only the requested page of items
        return items[start:end]

    # SR2 - Search and Filter Functionality
    def search_restaurants(self,q=None,restaurant_id=None,is_open=None,tag=None,page=None,page_size=None):
        # Get all restaurants from the repository
        restaurants = self.repo.get_all()

        # Filter by restaurant ID if provided
        if restaurant_id is not None:
            restaurants = [
                r for r in restaurants
                if str(r.get("restaurantId")) == restaurant_id or str(r.get("id")) == str(restaurant_id)
            ]

        # Filter by open/closed status if provided
        # From SR1, the repository sets isOpen = True for now
        if is_open is not None:
            restaurants = [
                r for r in restaurants
                if r.get("isOpen") == is_open
            ]

        # Tag filter
        if tag is not None:
            # Normalize by trimming spaces and making lowercase
            tag_norm = str(tag).strip().lower()

            # Reject empty tag input
            if tag_norm == "":
                raise ValueError("tag cannot be empty")

            # Keep only restaurants whose tags contain the given tag
            restaurants = [
                r for r in restaurants
                if tag_norm in str(r.get("tags", "")).lower()
            ]

        # Search filter
        if q is not None:
            # Normalize search input
            q_norm = str(q).strip().lower()

            # Empty search query returns no results
            if q_norm == "":
                restaurants = []
            else:
                # Helper function to check if query matches restaurant name
                # or any menu item name
                def matches(r):
                    name_ok = q_norm in str(r.get("name", "")).lower()
                    items = r.get("menuItems", [])
                    item_ok = any(
                        q_norm in str(it.get("name", "")).lower()
                        for it in items
                    )
                    return name_ok or item_ok

                # Keep only matching restaurants
                restaurants = [r for r in restaurants if matches(r)]

         restaurants = self.paginate(restaurants, page, page_size)
        return [self._to_schema_restaurant(r) for r in restaurants]