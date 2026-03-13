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
    # This is what the API layer will call
    def get_restaurants(self):

        restaurants = self.repo.get_all() # Call the repository to retrieve raw data

        # For now, we return it directly, until filtering and all is added
        return restaurants
    
    ''' SR2 STUFF - 
    Here we will implement some search and filter functionality 
    and there should be a unit test in the same commit to test this method '''    
    def search_restaurants(self, q=None, restaurant_id=None, is_open=None, tag=None):
        
        restaurants = self.repo.get_all() # Like above, call the repository to retrieve raw data

        # Here we match the restaurant to the argument passed in the endpoint
        if restaurant_id is not None: 
            restaurants = [r for r in restaurants if r.get("restaurantId") == restaurant_id] # So it filters out whatever IDs are irrelevant to the one passed in the endpoint

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
                raise ValueError("q cannot be empty")

            def matches(r):# But what if the user puts something in and we want to find a match
                name_ok = q_norm in str(r.get("name", "")).lower() # Confirm the name matches and if not just default to ""
                items = r.get("menuItems", []) # Grab menu items for our next step but default to empty otherwise to avoid errors
                item_ok = any(q_norm in str(it.get("name", "")).lower() for it in items) # Use any to match ANY searched item to anything on the menu.
                return name_ok or item_ok # Either or! Then we should have a match :)

            restaurants = [r for r in restaurants if matches(r)] # And of course, just show whatever meets either condition
            
        return restaurants