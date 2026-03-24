# import csv
# import os


# DATA_FILE = os.path.join("app", "data", "dataset.csv")


# def load_data():
#     restaurants = set()
#     menu_items = []

#     with open(DATA_FILE, newline="", encoding="utf-8") as file:
#         reader = csv.DictReader(file)

#         for row in reader:
#             restaurant_id = row["restaurant_id"]
#             restaurants.add(restaurant_id)

#             if row.get("menu_item_name"):
#                 menu_items.append({
#                     "restaurant_id": row["restaurant_id"],
#                     "name": row["menu_item_name"]
#                 })

#     return restaurants, menu_items


# def test_menu_items_have_valid_restaurant():
#     restaurants, menu_items = load_data()

#     for item in menu_items:
#         assert item["restaurant_id"] in restaurants


# def test_invalid_restaurant_reference():
#     restaurants, menu_items = load_data()

#     fake_item = {
#         "restaurant_id": "9999",
#         "name": "Fake Item"
#     }

#     assert fake_item["restaurant_id"] not in restaurants