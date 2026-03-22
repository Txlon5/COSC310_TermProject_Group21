# from app.schemas.menu import Menu, MenuCreate

# restaurants = [
#     {"id": 1, "name": "Burger Place"},
#     {"id": 2, "name": "Pizza Spot"},
#     {"id": 3, "name": "Sub Shop"}
# ]

# menus = [
#     Menu(id=1, restaurant_id=1, name="Burger", price=8.99),
#     Menu(id=2, restaurant_id=1, name="Fries", price=3.99),
#     Menu(id=3, restaurant_id=2, name="Pizza", price=12.99),
#     Menu(id=4, restaurant_id=2, name="Garlic Bread", price=4.99),
#     Menu(id=5, restaurant_id=3, name="Turkey Sub", price=9.49)
# ]

# def get_all_restaurants():
#     return restaurants

# def get_all_menus():
#     return menus

# def add_menu(menu_data: MenuCreate):
#     new_id = len(menus) + 1
#     new_menu = Menu(
#         id=new_id,
#         restaurant_id=menu_data.restaurant_id,
#         name=menu_data.name,
#         price=menu_data.price
#     )
#     menus.append(new_menu)
#     return new_menu

# def get_menu_items_by_restaurant(restaurant_id):
#     # Returns all menu items that belong to one restaurant.
#     return [item for item in menus if str(item.restaurant_id) == str(restaurant_id)]