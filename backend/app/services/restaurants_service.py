''' FULL DISCLAIMER
I need to have a chat with the team about how we will do tags.
As of right now, everyone is busy, but I have to continue working regardless.
So for now, SR2 will start like SR1, not using the CSV file, but working with mock data (for now) '''# Import the repository class
# The service will depend on the repository to retrieve data
from app.repositories.restaurants_repository import RestaurantsRepository


# This class represents the Business Logic Layer for restaurants
class RestaurantsService:

    def __init__(self, repo):
        # Store the repository instance inside the service
        # This allows the service to call repository methods
        self.repo = repo

    # Public method to get all restaurants
    # This is what the API layer calls
    def get_restaurants(self):

        restaurants = self.repo.get_all() # Call the repository to retrieve raw data

        # For now, we return it directly, until filtering and all is added
        return restaurants
    
    """THE BELOW FUNCTION IS FOR SR3 - PAGINATION"""
    def paginate(self, items, page, page_size): # Users can put in a page count and how many items they want per page
        # Below are some basic checks to make sure their parameters are valid
        if page is None or page_size is None:
            return items # If no pagination parameters are given, just return all items without paginating

        if page < 1:
            raise ValueError("page must be >= 1") # If given a page number less than 1 raise an error
        if page_size < 1:
            raise ValueError("pageSize must be >= 1") # If given a page size less than 1 raise an error

        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end] # Just return the slice of items that corresponds to the requested page and page size
     
    def search_restaurants(self, q=None, restaurant_id=None, is_open=None, tag=None, page=None, page_size=None):
    # SR2 - Search and Filter Functionality    
        restaurants = self.repo.get_all() # Like above, call the repository to retrieve raw data

        # Here we match the restaurant to the argument passed in the endpoint
        if restaurant_id is not None: 
            restaurants = [r for r in restaurants if r.get("restaurant_id") == restaurant_id] # So it filters out whatever IDs are irrelevant to the one passed in the endpoint

        ''' So I'm putting this here for the future. 
        I remember our team spoke about restaurants opening and closing,
        but we haven't agreed on putting those values yet. From SR1, the repository sets isOpen= True for now '''
        if is_open is not None:
            restaurants = [r for r in restaurants if r.get("isOpen") == is_open]

        # Tag filter (mockable in tests; real tags can come later)
        if tag is not None: # ie we DO have a tag of some kind
            tag_norm = str(tag).strip().lower() # "Normalize" it by removing whitespace and making it lowercase
            if tag_norm == "": # So we have a tag value, but it's just an empty string, which is not valid, then...
                raise ValueError("tag cannot be empty") # Raise an error! Amazing
            restaurants = [
                r for r in restaurants # So add the restaurant to the list IF
                if tag_norm in str(r.get("tags", "")).lower() # The restaurant has a "tags" field, and the normalized tag is found within it (case-insensitive)
            ]
            
        # Search filter
        if q is not None:
            q_norm = str(q).strip().lower() # Normalize as we did above for tags
            if q_norm == "": # May need to discuss with the team what should be done if no search query is provided, but for now, if it's just an empty string, we will raise an error
                return [] # I think this satisfies FEAT3-US1

            def matches(r):# But what if the user puts something in and we want to find a match
                name_ok = q_norm in str(r.get("name", "")).lower() # Confirm the name matches and if not just default to ""
                items = r.get("menuItems", []) # Grab menu items for our next step but default to empty otherwise to avoid errors
                item_ok = any(q_norm in str(it.get("name", "")).lower() for it in items) # Use any to match ANY searched item to anything on the menu.
                return name_ok or item_ok # Either or! Then we should have a match :)

            restaurants = [r for r in restaurants if matches(r)] # And of course, just show whatever meets either condition
            
        restaurants = self.paginate(restaurants, page, page_size)
            
        return restaurants
    
