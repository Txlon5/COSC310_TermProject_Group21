# Just writing a class list of dictionaries here, for testing purposes.
# Each dictionary also has a nested dictionary for menu items, each being a list of dictionaries open to expand
# I will work with the csv file soon, this is just for simplicity before Feat 2 is done.

RESTAURANTS = [
    {
        "restaurant_id": 1,
        "name": "Pizza Place",
        "tags": "Italian, Pizza",
        "isOpen": True,
        "menuItems": [
            {"menuItemId": 1, "name": "Pepperoni Pizza", "price": 15.99, "category": "Pizza"},
            {"menuItemId": 2, "name": "Veggie Pizza", "price": 13.99, "category": "Pizza"},
        ],
    },
    {
        "restaurant_id": 2,
        "name": "Burger House",
        "tags": "Fast Food, Burgers",
        "isOpen": False,
        "menuItems": [
            {"menuItemId": 3, "name": "Cheeseburger", "price": 11.99, "category": "Burger"},
        ],
    },
]