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
            "restaurantId": restaurant_id,
            "items": items,
            "status": "pending" # This is a default status for new orders, I will be able to set it to complete manually for testing
        }
        # We can update this later, but based on our current scrum meetings, and this is feat4 this is good enough for now

        self.orders.append(order) # Add the new order to the list
        self.next_id += 1 # Increment the ID counter for the next order

        return order

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