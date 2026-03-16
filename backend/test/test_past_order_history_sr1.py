from app.routers.orders import orders_store, notification, unauthorized_access_log
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_function():
    orders_store.clear()        #Clear orders from in-memory store before each test 
    notification.clear_notifications()      #Clear notifications before each test  
    unauthorized_access_log.clear()         # Clear unauthorized access log before each test    
    
def test_get_past_order_history_for_user_returns_empty_list():
    #verifies that APi returns empty list instead of an error when the user has no past order in history.
    response = client.get("/orders/history/no_orders_user", headers = {"X-User-Id": "no_orders_user"})
    assert response.status_code == 200
    assert response.json() == []        #Returned order history is an empty list
    
def test_get_past_order_history_returns_orders_for_that_user_only():
    #Verifies that order history belonging to a specific user is returned.
    order_1 = {"user_id": "user123", "restaurant_id": "restaurantA", "items": ["Nuggets"]}
    response_1 = client.post("/orders", json = order_1)
    assert response_1.status_code == 201
    
    order_2 = {"user_id": "user123", "restaurant_id": "restaurantB", "items": ["Burger"]}
    response_2 = client.post("/orders", json = order_2)
    assert response_2.status_code == 201
    
    order_3 = {"user_id": "user888", "restaurant_id": "restaurantC", "items": ["Pasta"]}
    response_3 = client.post("/orders", json = order_3)
    assert response_3.status_code == 201
    
    created_order_id_1 = response_1.json()["order_id"]      #extracts generated order IDs to later verify that correct orders were returned
    created_order_id_2 = response_2.json()["order_id"]
    created_order_id_3 = response_3.json()["order_id"]
    
    history_response = client.get("/orders/history/user123", headers = {"X-User-Id": "user123"})        #Retrieves order history for user123 and later converts to python data
    assert history_response.status_code == 200
    data = history_response.json()
    
    assert isinstance(data, list)
    assert len(data) == 2       #validates only two orders belong to user123
    
    returned_ids = {order["order_id"] for order in data}        
    assert returned_ids == {created_order_id_1, created_order_id_2}     #verifies orders returned matches user123 created orders
    assert created_order_id_3 not in returned_ids       #verifies another user order is not included.
    
    returned_restaurants = {order["restaurant_id"] for order in data}
    assert returned_restaurants == {"restaurantA", "restaurantB"}       #verifies correct restaurants are associated
    
    for order in data:
        assert order["user_id"] == "user123"
        assert "order_id" in order
        assert "restaurant_id" in order
        assert "items" in order
        assert "status" in order
        assert "created_at" in order
        assert "updated_at" in order
        assert "delivered_at" in order
        assert order["status"] == "Created"
        assert order["delivered_at"] is None
        
        
    