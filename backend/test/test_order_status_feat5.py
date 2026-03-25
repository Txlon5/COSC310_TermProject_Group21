import pytest
from fastapi.testclient import TestClient
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)
RESTAURANT_ID = "85590c53-fc55-4837-a3ef-283345df572a"

# Create mock admin for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )

# Test Setup - Setup Mock data/function calls for MenuItem Checks and Fetching/Saving Orders
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Set the auth override
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Mock Order Database
    fake_db = []
    # Mock MenuItems
    mock_menu_item1 = MagicMock()
    mock_menu_item1.menuItemId = 1
    mock_menu_item2 = MagicMock()
    mock_menu_item2.menuItemId = 2
    
     # Return mock list
    def mock_load():
        return fake_db.copy()
    
    # Save mock list
    def mock_save(data):
        fake_db.clear()
        fake_db.extend(data)

    # Apply mock functions
    with patch("app.services.orders_service.load_all", side_effect=mock_load), \
         patch("app.services.orders_service.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.fetch_menu_by_restaurant_id", return_value=[mock_menu_item1, mock_menu_item2]):
        yield

    # Clear the auth override after the test
    app.dependency_overrides = {}

def test_invalid_delivery_method():
    response = client.post("/orders", params={"delivery_method": "drone"}, json={
        "user_id": "u1",
        "card_id": "test-card-id",
        "restaurant_id":RESTAURANT_ID ,
        "items": [{"menuItemId": 1, "name": "Onion Pizza", "price": 26.0, "quantity": 1}],
    })
    assert response.status_code == 422


def test_delivery_without_address_is_currently_accepted():
    response = client.post("/orders", json={
        "user_id": "u1",
        "card_id": "test-card-id",
        "restaurant_id": RESTAURANT_ID,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
        "delivery_method": "delivery"
    })
    assert response.status_code == 201


def test_pickup_without_location_is_not_accepted():
    response = client.post("/orders", params={"delivery_method": "pickup"}, json={
        "user_id": "u1",
        "card_id": "test-card-id",
        "restaurant_id": 1,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}],
    })
    assert response.status_code == 422


def test_delivered_status_sets_timestamp():
    create = client.post("/orders", json={
        "user_id": "u1",
        "card_id": "test-card-id",
        "restaurant_id":  RESTAURANT_ID,
        "items": [{"menuItemId": 1,"name": "Onion Pizza", "price": 26.0, "quantity": 1}]
    })

    order_id = create.json()["order_id"]

    assert client.patch(f"/orders/{order_id}/status", json={"status": "preparing"}).status_code == 200
    assert client.patch(f"/orders/{order_id}/status", json={"status": "ready"}).status_code == 200
    response3 = client.patch(f"/orders/{order_id}/status", json={"status": "delivered"})
    assert response3.status_code == 200
    assert response3.json()["delivered_at"] is not None
