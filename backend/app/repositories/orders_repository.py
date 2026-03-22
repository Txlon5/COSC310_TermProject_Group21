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

def create_order(self, restaurant_id, items):
    order = {
        "orderId": self.next_id,
        "restaurant_id": restaurant_id, 
        "items": items,
        "status": "pending" # This is a default status for new orders, I will be able to set it to complete manually for testing
    }
    # We can update this later, but based on our current scrum meetings, and this is feat4 this is good enough for now


def get_order_by_id(self, order_id): # Retrieve an order by its ID
    for order in self.orders:
        if order["orderId"] == order_id:
            return order
    return None

"""
Potential feat5 integration later: We can add a method to update the status of an order (e.g., from 'pending' to 'completed' or 'delivered').
I spoke to Omarion on this, mock data is fine for now before we integrate.
Here we have a helper method to update order status
We can change this section later depending on delivery/pickup workflow.
"""
def mark_order_status(self, order_id, status):
    order = self.get_order_by_id(order_id)
    if order:
        order["status"] = status # Update the order's status


# Update an order's items or restaurantId, but prevent changes if status is 'completed'.
# Returns updated order if successful, raises ValueError if completed or not found.
def update_order(self, order_id, restaurant_id=None, items=None):
    order = self.get_order_by_id(order_id)
    if not order:
        raise ValueError("Order not found") # Quick error handling for order not found
    if order["status"] == "completed":
        raise ValueError("Cannot update a completed order") # Prevent updates to completed orders, our feat4-sr2
    if restaurant_id is not None:
        order["restaurant_id"] = restaurant_id # Update restaurant_id if provided
    if items is not None:
        order["items"] = items # Update items if provided
    return order
