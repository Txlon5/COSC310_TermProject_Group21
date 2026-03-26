from pathlib import Path
import json, os
from typing import List, Dict, Any

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

