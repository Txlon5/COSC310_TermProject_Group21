# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)


# def test_subtotal_single_item():
#     payload = {
#         "restaurant_id": "1",
#         "items": [
#             {
#                 "item_id": "1",
#                 "quantity": 1
#             }
#         ]
#     }

#     response = client.post("/order-cost/subtotal", json=payload)

#     assert response.status_code == 200
#     assert response.json() == {
#         "subtotal": 8.99
#     }


# def test_subtotal_multiple_items():
#     payload = {
#         "restaurant_id": "1",
#         "items": [
#             {
#                 "item_id": "1",
#                 "quantity": 2
#             },
#             {
#                 "item_id": "2",
#                 "quantity": 1
#             }
#         ]
#     }

#     # Burger 8.99 x 2 = 17.98
#     # Fries  3.99 x 1 = 3.99
#     # subtotal = 21.97

#     response = client.post("/order-cost/subtotal", json=payload)

#     assert response.status_code == 200
#     assert response.json() == {
#         "subtotal": 21.97
#     }


# def test_subtotal_quantity_change():
#     payload = {
#         "restaurant_id": "1",
#         "items": [
#             {
#                 "item_id": "2",
#                 "quantity": 3
#             }
#         ]
#     }

#     # Fries 3.99 x 3 = 11.97
#     response = client.post("/order-cost/subtotal", json=payload)

#     assert response.status_code == 200
#     assert response.json() == {
#         "subtotal": 11.97
#     }


# def test_subtotal_invalid_menu_item():
#     payload = {
#         "restaurant_id": "1",
#         "items": [
#             {
#                 "item_id": "999",
#                 "quantity": 1
#             }
#         ]
#     }

#     response = client.post("/order-cost/subtotal", json=payload)

#     assert response.status_code == 404
#     assert "not found" in response.json()["detail"].lower()


# def test_subtotal_invalid_restaurant():
#     payload = {
#         "restaurant_id": "999",
#         "items": [
#             {
#                 "item_id": "1",
#                 "quantity": 1
#             }
#         ]
#     }

#     response = client.post("/order-cost/subtotal", json=payload)

#     assert response.status_code == 404
#     assert response.json()["detail"] == "No menu items found for restaurant"