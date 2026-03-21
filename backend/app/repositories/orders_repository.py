from pathlib import Path
import json, os
from typing import List, Dict, Any


"""
Feat4-SR1
The system shall allow users to create food orders

Stores and retrieves food orders.
Orders are persisted in memory while the server is running
"""

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "orders.json"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_all(users: List[Dict[str, Any]]) -> None:
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

        
    # def __init__(self):
    #     self.orders = []  # List to store order dictionaries
    #     self.next_id = 1  # Counter for assigning unique order IDs

    # def create_order(self, restaurant_id, items):
    #     order = {
    #         "orderId": self.next_id,
    #         "restaurant_id": restaurant_id,
    #         "items": items,}

    #     self.orders.append(order) # Add the new order to the list
    #     self.next_id += 1 # Increment the ID counter for the next order

    #     return order

    # def get_order_by_id(self, order_id): # Retrieve an order by its ID
    #     for order in self.orders:
    #         if order["orderId"] == order_id:
    #             return order
    #     return None