from fastapi import HTTPException
from app.repositories.restaurants_repository import RestaurantsRepository
from app.schemas.menu import MenuItem, CreateMenuItem
from app.schemas.restaurant import Restaurant


def fetch_all_menus():
    restaurant_repo = RestaurantsRepository()
    restaurants = restaurant_repo.load_all()

    all_menus = []
    for it in restaurants:
        restaurant = Restaurant(**it)
        all_menus.append({
            "restaurant_id": restaurant.restaurant_id,
            "menuItems": restaurant.menuItems
        })
    return all_menus

def fetch_menu_by_restaurant_id(restaurant_id: str):
    restaurant_repo = RestaurantsRepository()
    restaurants = restaurant_repo.load_all()

    for it in restaurants:
        if it.get("restaurant_id") == restaurant_id:
            return Restaurant(**it).menuItems
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")


def create_menu_item(restaurant_id: str, payload: CreateMenuItem) -> MenuItem:
    restaurant_repo = RestaurantsRepository()
    restaurants = restaurant_repo.load_all()

    for r in restaurants:
            if r.get("restaurant_id") == restaurant_id:
                # Get list of menu items
                menu_items = r.get("menuItems", [])

                # Fetch new_item values
                new_id = len(menu_items) + 1
                new_name = payload.name.strip()
                new_price = payload.price
                new_category = payload.category.strip()
                
                # Create new menu item
                new_item = MenuItem(
                     menuItemId=new_id,
                     name=new_name,
                     price= new_price,
                     category= new_category,
                )

                # Convert back to dictionary and add to menu list
                menu_items.append(new_item.model_dump())

                # Assign restaurant with new menu list and save
                r["menuItems"] = menu_items
                restaurant_repo.save_all(restaurants)

                # Return new_item created to user
                return new_item

            
    raise HTTPException(status_code=400, detail="Restaurant does not exist")

        




    # for restaurant in restaurants:
    #     if restaurant["id"] == menu_data.restaurant_id:
    #         restaurant_exists = True
    #         break

    # if not restaurant_exists:
    #     raise HTTPException(status_code=400, detail="Restaurant does not exist")

    # return add_menu(menu_data)
