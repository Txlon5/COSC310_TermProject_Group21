import csv # Implementing our CSV parsing logic
from pathlib import Path

"""
This file is responsible for reading the CSV file and converting it into a list of restaurant dictionaries with the structure we want. 
The RestaurantsService will then use this repository to get the data it needs to filter and return to the API layer. The structure of 
the restaurant dictionaries is designed to match what we expect in our service and API layers, with fields like restaurant_id, name, 
tags, isOpen, and menuItems.
"""

class RestaurantsRepository:
    def __init__(self, csv_path=None):
        # If no path is provided, load backend/app/data/dataset.csv, that should be where we keep the CSV file anwyay
        if csv_path is None:
            csv_path = Path(__file__).resolve().parent.parent / "data" / "dataset.csv" # So from this file, go up twice ie from .py to repositories to app, then down to data then the CSV file
        self.csv_path = Path(csv_path) # We probably won't have one set but this is here anyway for modularity

    def get_all(self):
 
        restaurants_map = {}

        seen_items = {} # Track which food items we've already added per restaurant (avoid duplicates)

        # Open CSV and read rows as dictionaries
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                
                rid = int(row["restaurant_id"]) # Read restaurant id from CSV
                
                # Create the restaurant entry the first time we see this rid
                if rid not in restaurants_map:
                    restaurants_map[rid] = {
                        
                        "restaurant_id": rid,
                        
                        "name": (row.get("restaurant_name", f"Restaurant {rid}") or f"Restaurant {rid}").strip(),
                        
                        "tags": (row.get("tags", "") or "").strip(),
                        
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

        # Return list of restaurants (sorted by restaurant_id for stable output)
        return [restaurants_map[k] for k in sorted(restaurants_map.keys())]