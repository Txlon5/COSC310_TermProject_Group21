"""
Feat4-SR1
The system shall allow users to create food orders

This file contains business logic for creating and retrieving orders.
Here, we can:
- Validate order contents
- Ensure an order has at least one item
- Delegate persistence/retrieval to the repository
"""

class OrdersService:
    def __init__(self, repo):
        self.repo = repo

    def create_order(self, user_id, restaurant_id, items):
        # Order must contain at least one item
        if not items or len(items) == 0:
            raise ValueError("Order must contain at least one item") # Quick error handling

        return self.repo.create_order(user_id, restaurant_id, items) #Give it to the repository to store and return the created order

    def get_order_by_id(self, order_id):
        # Retrieve the order from the repository
        order = self.repo.get_order_by_id(order_id)

        if order is None:
            raise ValueError("Order not found") # Quick error handling for not found

        return order # Return the found order