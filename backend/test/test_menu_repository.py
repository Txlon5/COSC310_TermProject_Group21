from app.repositories import menu_repository
from app.schemas.menu import MenuCreate, Menu
from app.schemas.restaurant import RestaurantCreate, Restaurant


def setup_function():
    menu_repository.menus[:] = [
        Menu(id=1, restaurant_id=1, name="Burger", price=8.99),
        Menu(id=2, restaurant_id=1, name="Fries", price=3.99),
        Menu(id=3, restaurant_id=2, name="Pizza", price=12.99),
        Menu(id=4, restaurant_id=2, name="Garlic Bread", price=4.99),
        Menu(id=5, restaurant_id=3, name="Turkey Sub", price=9.49),
    ]

    menu_repository.restaurants[:] = [
        Restaurant(id=1, name="Burger Place", category="Fast Food", tags=["Burgers"]),
        Restaurant(id=2, name="Pizza Spot", category="Italian", tags=["Pizza"]),
        Restaurant(id=3, name="Sub Shop", category="Turkish", tags=["Sandwich"]),
    ]


def test_get_all_restaurants_returns_restaurants():
    restaurants = menu_repository.get_all_restaurants()

    assert isinstance(restaurants, list)
    assert len(restaurants) == 3
    assert restaurants[0]["id"] == 1


def test_get_all_menus_returns_menus():
    menus = menu_repository.get_all_menus()

    assert isinstance(menus, list)
    assert len(menus) == 5
    assert menus[0].name == "Burger"


def test_add_menu_adds_new_menu_item():
    new_menu_data = MenuCreate(
        restaurant_id=1,
        name="Onion Rings",
        price=5.99
    )

    new_menu = menu_repository.add_menu(new_menu_data)

    assert new_menu.id == 6
    assert new_menu.restaurant_id == 1
    assert new_menu.name == "Onion Rings"
    assert len(menu_repository.menus) == 6


def test_add_menu_appends_to_menu_list():
    new_menu_data = MenuCreate(
        restaurant_id=2,
        name="Cheese Pizza Slice",
        price=6.50
    )

    new_menu = menu_repository.add_menu(new_menu_data)

    assert menu_repository.menus[-1] == new_menu


def test_add_restaurant_returns_new_restaurant():
    original_count = len(menu_repository.restaurants)

    new_restaurant = RestaurantCreate(
        name="Taco Town",
        category="Mexican",
        tags=["Tacos", "Burritos"]
    )

    result = menu_repository.add_restaurant(new_restaurant)

    assert result.id == original_count + 1
    assert result.name == "Taco Town"
    assert result.category == "Mexican"
    assert result.tags == ["Tacos", "Burritos"]


def test_add_restaurant_appends_to_restaurants_list():
    original_count = len(menu_repository.restaurants)

    new_restaurant = RestaurantCreate(
        name="Sushi Place",
        category="Japanese",
        tags=["Sushi"]
    )

    result = menu_repository.add_restaurant(new_restaurant)

    assert len(menu_repository.restaurants) == original_count + 1
    assert menu_repository.restaurants[-1].id == result.id
    assert menu_repository.restaurants[-1].name == "Sushi Place"
    assert menu_repository.restaurants[-1].category == "Japanese"
    assert menu_repository.restaurants[-1].tags == ["Sushi"]


def test_add_restaurant_assigns_incremented_id():
    starting_last_id = menu_repository.restaurants[-1].id

    new_restaurant = RestaurantCreate(
        name="Pasta Corner",
        category="Italian",
        tags=["Pasta"]
    )

    result = menu_repository.add_restaurant(new_restaurant)

    assert result.id == starting_last_id + 1