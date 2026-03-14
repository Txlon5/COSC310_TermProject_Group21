from app.routers.orders import orders_store, notification
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_function():
    orders_store.clear()
    notification.clear_notifications()
    
def test_get_past_order_history_for_user_returns_empty_list():
    response = client.get("/orders/history/no_orders_user")
    assert response.status_code == 200
    assert response.json() == []
    
def test_get_past_order_history_returns_orders_for_that_user_only():
    order_1 = {"user_id": "user123", "restaurant_id": "restaurantA", "items": ["Nuggets"]}
    response_1 = client.post("/orders", json = order_1)
    assert response_1.status_code ==201
    
    order_2 = {"user_id": "user123", "restaurant_id": "restaurantB", "items": ["Burger"]}
    response_2 = client.post("/orders", json = order_2)
    assert response_2.status_code ==201
    
    order_3 = {"user_id": "user888", "restaurant_id": "restaurantC", "items": ["Pasta"]}
    response_3 = client.post("/orders", json = order_3)
    assert response_3.status_code ==201
    
    history_response = client.get("/orders/history/user123")
    assert history_response.status_code == 200
    
    data = history_response.json()
    assert len(data) == 2
    
    for order in data:
        assert order["user_id"] == "user123"
        
def test_get_order_history_returns_empty_list_for_user_with_no_orders():
    response = client.get("/orders/history/no_orders_users")
    assert response.status_code == 200
    assert response.json() == []
    