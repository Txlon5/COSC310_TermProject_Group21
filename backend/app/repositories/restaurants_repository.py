import csv # Implementing our CSV parsing logic
from pathlib import Path
import json, os
from typing import List, Dict, Any

"""
This file is responsible for reading the CSV file and converting it into a list of restaurant dictionaries with the structure we want. 
The RestaurantsService will then use this repository to get the data it needs to filter and return to the API layer. The structure of 
the restaurant dictionaries is designed to match what we expect in our service and API layers, with fields like restaurant_id, name, 
tags, isOpen, and menuItems.
"""

class RestaurantsRepository:
    def __init__(self, json_path=None):
        # If no path is provided, load backend/app/data/restaurants.json, that should be where we keep the Json file anwyay
        if json_path is None:
            json_path = Path(__file__).resolve().parents[1] / "data" / "restaurants.json" # So from this file, go up twice ie from .py to repositories to app, then down to data then the json file
        self.json_path = Path(json_path) # We probably won't have one set but this is here anyway for modularity
        self._restaurants = None
    
    def load_all(self) -> List[Dict[str, Any]]:
        if not self.json_path.exists():
            return []
        with self.json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_all(self, restaurants: List[Dict[str, Any]]) -> None:
        tmp = self.json_path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(restaurants, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.json_path)


# class RestaurantsRepository:
#     def __init__(self, csv_path=None):
#         # If no path is provided, load backend/app/data/dataset.csv, that should be where we keep the CSV file anwyay
#         if csv_path is None:
#             csv_path = Path(__file__).resolve().parent.parent / "data" / "dataset.csv" # So from this file, go up twice ie from .py to repositories to app, then down to data then the CSV file
#         self.csv_path = Path(csv_path) # We probably won't have one set but this is here anyway for modularity
#         self._restaurants = None
        
#     def save_all(self, restaurants):
#         self._restaurants = restaurants


#     def get_all(self):
#         restaurants_map = {}
#         seen_items = {}
#         if self._restaurants is not None:
#             return self._restaurants
#         with self.csv_path.open("r", encoding="utf-8", newline="") as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 rid = int(row["restaurant_id"])
#                 restaurant_name = row.get("restaurant_name", f"Restaurant {rid}").strip()
#                 tags = row.get("tags", "").strip()
#                 tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
#                 if rid not in restaurants_map:
#                     restaurants_map[rid] = {
#                         "restaurant_id": rid,
#                         "restaurant_name": restaurant_name,
#                         "tags": tag_list,
#                         "isOpen": True,
#                         "menuItems": [],
#                     }
#                     seen_items[rid] = set()
#                 else:
#                     # Always update restaurant_name and tags if new row has them
#                     if restaurant_name:
#                         restaurants_map[rid]["restaurant_name"] = restaurant_name
#                     if tag_list:
#                         restaurants_map[rid]["tags"] = tag_list
#                 item_name = row.get("food_item", "").strip()
#                 if item_name == "":
#                     continue
#                 if item_name in seen_items[rid]:
#                     continue
#                 next_id = len(restaurants_map[rid]["menuItems"]) + 1
#                 # Use the first tag as the category if available
#                 item_category = tag_list[0] if tag_list else "Unknown"
#                 restaurants_map[rid]["menuItems"].append({
#                     "menuItemId": next_id,
#                     "name": item_name,
#                     "price": 0.0,
#                     "category": item_category,
#                 })
#                 seen_items[rid].add(item_name)
#         self._restaurants = [restaurants_map[k] for k in sorted(restaurants_map.keys())]
#         return self._restaurants