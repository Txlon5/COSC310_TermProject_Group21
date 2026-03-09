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
    def __init__(self, repo, restaurants_repo):
        self.repo = repo
        self.restaurants_repo = restaurants_repo

    def create_order(self, restaurant_id, items):
        # Order must contain at least one item
        if not items or len(items) == 0:
            raise ValueError("Order must contain at least one item")

        # Validate menuItemIds against restaurant's menuItems
        restaurants = self.restaurants_repo.get_all()
        restaurant = next((r for r in restaurants if r["restaurantId"] == restaurant_id), None)
        if not restaurant:
            raise ValueError("Restaurant not found")

        valid_menu_ids = {item["menuItemId"] for item in restaurant["menuItems"]}
        for order_item in items:
            if order_item["menuItemId"] not in valid_menu_ids:
                raise ValueError(f"Invalid menuItemId: {order_item['menuItemId']} for restaurant {restaurant_id}")

        return self.repo.create_order(restaurant_id, items)

    def get_order_by_id(self, order_id):
        # Retrieve the order from the repository
        order = self.repo.get_order_by_id(order_id)

        if order is None:
            raise ValueError("Order not found") # Quick error handling for not found

        return order # Return the found order