"""
Feat4-SR1
The system shall allow users to create food orders

Stores and retrieves food orders.
Orders are persisted in memory while the server is running
"""

class OrdersRepository:
    def __init__(self):
        self.orders = []  # List to store order dictionaries
        self.next_id = 1  # Counter for assigning unique order IDs

    def create_order(self, restaurant_id, items):
        order = {
            "orderId": self.next_id,
            "restaurant_id": restaurant_id,
            "items": items,}
        # We can update this later, but based on our current scrum meetings, and this is feat4 this is good enough for now

        self.orders.append(order) # Add the new order to the list
        self.next_id += 1 # Increment the ID counter for the next order

        return order

    def get_order_by_id(self, order_id): # Retrieve an order by its ID
        for order in self.orders:
            if order["orderId"] == order_id:
                return order
        return None