import csv # Implementing our CSV parsing logic
from pathlib import Path

''' I do want to note, "rid" refers to restaurant_id from the CSV, 
and "item_name" is the food_item column from the CSV. The rest of the fields 
are generated or default values since the CSV doesn't provide them. This is 
just a starting point, and we can change it later as needed.'''

class RestaurantsRepository:
    def __init__(self, csv_path=None):
        # If no path is provided, load backend/app/data/dataset.csv, that should be where we keep the CSV file anwyay
        if csv_path is None:
            csv_path = Path(__file__).resolve().parent.parent / "data" / "dataset.csv" # So from this file, go up twice ie from .py to repositories to app, then down to data then the CSV file
        self.csv_path = Path(csv_path) # We probably won't have one set but this is here anyway for modularity
        self._restaurants = None
        
    def save_all(self, restaurants):
        self._restaurants = restaurants


    def get_all(self):
        # restaurants_map will look like:
        # { 16: {"restaurantId":16, "name":"Restaurant 16", ..., "menuItems":[...]}, ... }
        # We do need to update parts of it like restaurant names and tags soon, but this is the general structure for now.
        restaurants_map = {}

        seen_items = {} # Track which food items we've already added per restaurant (avoid duplicates)
        if self._restaurants is not None:
            return self._restaurants
        # Open CSV and read rows as dictionaries
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                
                rid = int(row["restaurant_id"]) # Read restaurant id from CSV
                
                # Create the restaurant entry the first time we see this rid
                if rid not in restaurants_map:
                    restaurants_map[rid] = {
                        
                        "restaurantId": rid,
                        
                        "name": f"Restaurant {rid}", # CSV doesn't provide a restaurant name, so we generate one
                        
                        "tags": [], # CSV doesn't provide tags; keep consistent with schema
                        
                        "isOpen": True, # CSV doesn't provide open/closed; default True for now
                        
                        "menuItems": [], # Menu items list (built from unique food_item values)
                    }
                    seen_items[rid] = set()

                # Use food_item as a "menu item" identifier (unique per restaurant)
                item_name = row.get("food_item", "").strip() # Directly grabbing the food item as item name
                if item_name == "":
                    continue # Skip empty item names (I don't think we have any, but just to be safe)

                if item_name in seen_items[rid]:
                    continue  # Skip, as we already added this item for this restaurant

                next_id = len(restaurants_map[rid]["menuItems"]) + 1 # Just incrementing each new item for this restaurant

                # CSV doesn't contain item category/price; use defaults
                restaurants_map[rid]["menuItems"].append(
                    {
                        "menuItemId": next_id,
                        "name": item_name,
                        "price": 0.0,
                        "category": "Unknown",
                    }
                )
                seen_items[rid].add(item_name)

        # Return list of restaurants (sorted by restaurantId for stable output)
        self._restaurants = [restaurants_map[k] for k in sorted(restaurants_map.keys())]
        return self._restaurants