import uuid  # Used to generate a unique ID for newly created restaurants
from fastapi import HTTPException  # Used to raise API-friendly errors
from app.repositories.restaurants_repository import RestaurantsRepository  # Repository layer for restaurant data
from app.schemas.restaurant import Restaurant, RestaurantUpdate, RestaurantMinimal

# This class represents the Business Logic Layer for restaurants.
# The router talks to this service, and this service talks to the repository.
class RestaurantsService:
    def __init__(self, repo: RestaurantsRepository):
        # Store the repository instance inside the service
        # This allows the service to call repository methods
        self.repo = repo

    # Public method to get all restaurants
    # This is what the API layer will call

    # Omarion
    # Get all restaurants - return with minimal values (id, name, tags)
    def list_restaurants(self):
        return [RestaurantMinimal(**it) for it in self.repo.load_all()]
    
    # Tariq
    # Get all restaurants - full data
    def get_restaurants(self):
        return [Restaurant(**it) for it in self.repo.load_all()]
    
    # Omarion
    # Get Restaurant by Id
    def get_restaurant_by_id(self, restaurant_id: str) -> Restaurant:
        # Get list of all restaurants and cast to Restaurant schema
        restaurants = self.repo.load_all()

        # Search list for restaurant by id
        for r in restaurants:
            if str(r.get("restaurant_id")) == str(restaurant_id):
                # Return restaurant
                return Restaurant(**r)
        # Error restaurant does not exist
        raise HTTPException(status_code=404,detail=f"Restaurant '{restaurant_id}' not found")
    
    # Omarion
    # Creates a new restaurant and appends it to the current restaurant list
    def create_restaurant(self, payload):
        # Load in existing restaurant list
        restaurants = self.repo.load_all()

        # Create restaurant
        new_restaurant = Restaurant(
            restaurant_id = str(uuid.uuid4()),
            restaurant_name = payload.restaurant_name.strip(),
            tags = payload.tags if payload.tags is not None else [],
            isOpen = bool(payload.isOpen),
            menuItems = []
        )

        # Add new_restaurant to restaurant list and save changes
        restaurants.append(new_restaurant.model_dump(mode='json'))
        self.repo.save_all(restaurants)

        # Return new_restaurant to user
        return new_restaurant
    
    # Omarion
    # Updates an existing restaurant by ID
    def update_restaurant(self, update_restaurant_id: str, payload: RestaurantUpdate) -> Restaurant:
        restaurants = self.repo.load_all()
        
        # Search restaurant list for restaurant associated with update_restaurant_id
        for idx, r in enumerate(restaurants):
            # Check if update_restaurant_id matches
            if str(r.get("restaurant_id")) == str(update_restaurant_id):
                # Update fields if entered
                if payload.restaurant_name is not None and payload.restaurant_name.strip() != "":
                    r["restaurant_name"] = payload.restaurant_name.strip()
                if payload.tags is not None and payload.tags != []:
                    r["tags"] = payload.tags
                if payload.isOpen is not None:
                    r["isOpen"] = payload.isOpen

                # Save changes to restaurant list
                restaurants[idx] = r
                self.repo.save_all(restaurants)

                # Return restaurant
                return Restaurant(**r)
        # Throw exception if restaurant does not exist
        raise HTTPException(status_code=404,detail=f"Restaurant '{update_restaurant_id}' not found")

    # Omarion
    # Deletes a restaurant by ID
    def delete_restaurant(self, restaurant_id: str):
        restaurants = self.repo.load_all()

        for idx, r in enumerate(restaurants):
            if str(r.get("restaurant_id")) == str(restaurant_id):
                # Remove restaurant entry
                restaurants.pop(idx)

                # Save restaurant list changes
                self.repo.save_all(restaurants)
                return

        raise HTTPException(status_code=404,detail=f"Restaurant '{restaurant_id}' not found")

    # Tariq
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

    # Tariq
    # SR2 - Search and Filter Functionality
    def search_restaurants(self,q=None,restaurant_id=None,is_open=None,tag=None,page=None,page_size=None):
        # Get all restaurants from the repository
        restaurants = self.repo.load_all()

        # Filter by restaurant ID if provided
        if restaurant_id is not None:
            restaurants = [
                r for r in restaurants
                if str(r.get("restaurant_id")) == str(restaurant_id) or str(r.get("id")) == str(restaurant_id)
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
                raise HTTPException(status_code=400, detail="tag cannot be empty")

            def has_tag(r):
                tags = r.get("tags", [])

                 # If tags is a string, convert it into a list
                if isinstance(tags, str):
                    tags = [t.strip() for t in tags.split(",") if t.strip()]
                    
                return any(tag_norm == str(t).strip().lower() for t in tags)
            restaurants = [r for r in restaurants if has_tag(r)]

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
                    name_ok = q_norm in str(r.get("restaurant_name", "")).lower()
                    items = r.get("menuItems", [])
                    item_ok = any(
                        q_norm in str(it.get("name", "")).lower()
                        for it in items
                    )
                    return name_ok or item_ok

                # Keep only matching restaurants
                restaurants = [r for r in restaurants if matches(r)]

        restaurants = self.paginate(restaurants, page, page_size)
        return [Restaurant(**r) for r in restaurants]
    
    # Tariq
    def get_restaurant_filtered(self,q=None,restaurant_id=None,is_open=None,tag=None,page=None,page_size=None):
        if q is not None and str(q).strip() == "":
            raise HTTPException(status_code=400, detail="q cannot be empty")

        if q is None and restaurant_id is None and is_open is None and tag is None and page is None and page_size is None:
            return self.get_restaurants()

        return self.search_restaurants(
            q=q,
            restaurant_id=restaurant_id,
            is_open=is_open,
            tag=tag,
            page=page,
            page_size=page_size,
        )
