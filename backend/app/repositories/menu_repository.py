from app.schemas.menu import Menu, MenuCreate
from app.schemas.restaurant import Restaurant, RestaurantCreate

restaurants = [
    Restaurant(id=1, name="Burger Place", category="Fast Food", tags=["Burgers"]),
    Restaurant(id=2, name="Pizza Spot", category="Italian", tags=["Pizza"]),
    Restaurant(id=3, name="Sub Shop", category="Turkish", tags=["Sandwich"]),
]

menus = [
    Menu(id=1, restaurant_id=1, name="Burger", price=8.99),
    Menu(id=2, restaurant_id=1, name="Fries", price=3.99),
    Menu(id=3, restaurant_id=2, name="Pizza", price=12.99),
    Menu(id=4, restaurant_id=2, name="Garlic Bread", price=4.99),
    Menu(id=5, restaurant_id=3, name="Turkey Sub", price=9.49),
]


def get_all_restaurants():
    return [restaurant.model_dump() for restaurant in restaurants]


def get_all_menus():
    return menus


def add_menu(menu_data: MenuCreate):
    new_id = len(menus) + 1

    new_menu = Menu(
        id=new_id,
        restaurant_id=menu_data.restaurant_id,
        name=menu_data.name,
        price=menu_data.price,
    )

    menus.append(new_menu)
    return new_menu


def add_restaurant(restaurant_data: RestaurantCreate):
    new_id = len(restaurants) + 1

    new_restaurant = Restaurant(
        id=new_id,
        name=restaurant_data.name,
        category=restaurant_data.category,
        tags=restaurant_data.tags,
    )

    restaurants.append(new_restaurant)
    return new_restaurant