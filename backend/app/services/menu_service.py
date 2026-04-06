from fastapi import HTTPException
from app.repositories.restaurants_repository import RestaurantsRepository
from app.schemas.menu import MenuItem, CreateMenuItem, UpdateMenuItem
from app.schemas.restaurant import Restaurant


# Omarion
class MenuService:
    def __init__(self):
        self.restaurant_repo = RestaurantsRepository()

    def fetch_all_menus(self):
        restaurants = self.restaurant_repo.load_all()
        menus = []

        for restaurant_data in restaurants:
            restaurant = Restaurant(**restaurant_data)
            menus.append({
                "restaurant_id": restaurant.restaurant_id,
                "menuItems": [item.model_dump() for item in restaurant.menuItems]
            })

        return menus

    def fetch_menu_by_restaurant_id(self, restaurant_id: str):
        restaurants = self.restaurant_repo.load_all()

        for restaurant_data in restaurants:
            if str(restaurant_data.get("restaurant_id")) == str(restaurant_id):
                restaurant = Restaurant(**restaurant_data)
                return restaurant.menuItems

        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

    def _get_next_menu_item_id(self, menu_items):
        biggest_id = 0

        for item in menu_items:
            current_id = int(item.get("menuItemId", 0))
            if current_id > biggest_id:
                biggest_id = current_id

        return biggest_id + 1

    def create_menu_item(self, restaurant_id: str, payload: CreateMenuItem) -> MenuItem:
        restaurants = self.restaurant_repo.load_all()

        for restaurant in restaurants:
            if str(restaurant.get("restaurant_id")) == str(restaurant_id):
                menu_items = restaurant.get("menuItems", [])

                name = payload.name.strip()
                category = payload.category.strip()
                price = payload.price

                if name == "":
                    raise HTTPException(status_code=400, detail="Menu item name cannot be empty")
                if category == "":
                    raise HTTPException(status_code=400, detail="Category cannot be empty")
                if price <= 0:
                    raise HTTPException(status_code=400, detail="Price must be greater than 0")

                new_item = MenuItem(
                    menuItemId=self._get_next_menu_item_id(menu_items),
                    name=name,
                    price=price,
                    category=category,
                )

                menu_items.append(new_item.model_dump())
                restaurant["menuItems"] = menu_items
                self.restaurant_repo.save_all(restaurants)
                return new_item

        raise HTTPException(status_code=400, detail="Restaurant does not exist")

    def update_menu_item(self, restaurant_id: str, menu_item_id: int, payload: UpdateMenuItem):
        restaurants = self.restaurant_repo.load_all()

        for restaurant in restaurants:
            if str(restaurant.get("restaurant_id")) == str(restaurant_id):
                menu_items = restaurant.get("menuItems", [])

                for item in menu_items:
                    if int(item.get("menuItemId")) == int(menu_item_id):
                        name = payload.name.strip()
                        category = payload.category.strip()
                        price = payload.price

                        if name == "":
                            raise HTTPException(status_code=400, detail="Menu item name cannot be empty")
                        if category == "":
                            raise HTTPException(status_code=400, detail="Category cannot be empty")
                        if price <= 0:
                            raise HTTPException(status_code=400, detail="Price must be greater than 0")

                        item["name"] = name
                        item["price"] = price
                        item["category"] = category

                        self.restaurant_repo.save_all(restaurants)
                        return item

                raise HTTPException(status_code=404, detail="Menu item not found")

        raise HTTPException(status_code=404, detail="Restaurant not found")

    def delete_menu_item(self, restaurant_id: str, menu_item_id: int):
        restaurants = self.restaurant_repo.load_all()

        for restaurant in restaurants:
            if str(restaurant.get("restaurant_id")) == str(restaurant_id):
                menu_items = restaurant.get("menuItems", [])

                for index, item in enumerate(menu_items):
                    if int(item.get("menuItemId")) == int(menu_item_id):
                        menu_items.pop(index)
                        restaurant["menuItems"] = menu_items
                        self.restaurant_repo.save_all(restaurants)
                        return

                raise HTTPException(status_code=404, detail="Menu item not found")

        raise HTTPException(status_code=404, detail="Restaurant not found")


_menu_service = MenuService()


def fetch_all_menus():
    return _menu_service.fetch_all_menus()



def fetch_menu_by_restaurant_id(restaurant_id: str):
    return _menu_service.fetch_menu_by_restaurant_id(restaurant_id)



def create_menu_item(restaurant_id: str, payload: CreateMenuItem):
    return _menu_service.create_menu_item(restaurant_id, payload)



def update_menu_item(restaurant_id: str, menu_item_id: int, payload: UpdateMenuItem):
    return _menu_service.update_menu_item(restaurant_id, menu_item_id, payload)



def delete_menu_item(restaurant_id: str, menu_item_id: int):
    return _menu_service.delete_menu_item(restaurant_id, menu_item_id)
