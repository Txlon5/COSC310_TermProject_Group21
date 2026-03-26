from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime, timezone
from app.main import app
from app.auth.token_utils import get_current_user
from app.schemas.user import User
from app.schemas.payment_method import CreditCard
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusType, PaymentUpdate
from app.services.payments_service import get_card_for_user as fake_get_card
from app.services.payments_service import create_transaction as fake_create_payment
from app.services.payments_service import update_transaction as fake_update_payment
from app.repositories.transactions_repository import save_all as save_transactions
from app.repositories.payment_methods_repository import save_all as save_cards
import pytest
client = TestClient(app)


# Test Preparation

# Create mock admin for testing
def override_get_current_user():
    return User(
        id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        name="Admin",
        email="admin@example.com",
        password="password123!",
        role="admin"
    )

# Override get_current_user() to return mock admin
@pytest.fixture(autouse=True)
def apply_admin_override():
    # Set the override
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Pause to allow test to run with override
    yield 
    # Clear the override after test is done
    app.dependency_overrides = {}

# Isolate tests from real transaction and card data
@pytest.fixture(autouse=True)
def isolated_repos(monkeypatch, tmp_path):
    monkeypatch.setattr("app.repositories.transactions_repository.DATA_PATH", tmp_path / "transactions.json")
    monkeypatch.setattr("app.repositories.payment_methods_repository.DATA_PATH", tmp_path / "payment_methods.json")
    save_transactions([])
    save_cards([])

# Test card for calls
TEST_CARD = {
    "card_num": "4868719196829038",
    "card_cvc": "344",
    "card_exp": "2029-11",
    "holder_name": "John Smith",
    "holder_address": "556 Sarsons Rd, V1W5H5, Kelowna, BC"
}

# Test card data for mock transactions
TEST_CARD_DATA = {
    "id": "card-1",
    "user_id": "8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
    "card_num": "4868719196829038",
    "card_cvc": "344",
    "card_exp": "2029-11",
    "holder_name": "Admin User",
    "holder_address": "123 Admin St"
}

# Create test card and return id
def create_test_card():
    r = client.post("/payments/cards/", json=TEST_CARD)
    assert r.status_code == 201
    return r.json()["id"]

# Create fake transaction
def make_transaction(order_id, user_id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7", status="pending"):
    return {
        "payment_id": f"pay-{order_id}",
        "order_id": order_id,
        "user_id": user_id,
        "card": TEST_CARD_DATA,
        "status": status,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "price_total": 25.00
    }


# Integration Tests

# Transaction Retrieval by Order ID - Valid
def test_get_transaction():
    fake_transactions = [make_transaction("order-1")]

    with patch("app.services.payments_service.transaction_repo.load_all", return_value=fake_transactions):
        r = client.get("/payments/order-1")
        assert r.status_code == 200

        # Save json response to variable
        data = r.json()

        # Check returned data matches input
        assert data["order_id"] == "order-1"
        assert data["card"]["card_cvc"] == "***"                        

# Transaction Retrieval by Order ID - Not Found
def test_get_transaction_na():
    with patch("app.services.payments_service.transaction_repo.load_all", return_value=[]):
        r = client.get("/payments/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

# Transaction Retrieval by Order ID - Unauthorized
def test_get_transaction_unauthorized():
    fake_transactions = [make_transaction("order-1", user_id="other-user-id")]

    with patch("app.services.payments_service.transaction_repo.load_all", return_value=fake_transactions):
        r = client.get("/payments/order-1")
        assert r.status_code == 403

# Transaction Status Retrieval - Valid
def test_get_transaction_status():
    fake_transactions = [make_transaction("order-1")]

    with patch("app.services.payments_service.transaction_repo.load_all", return_value=fake_transactions):
        r = client.get("/payments/status/order-1")
        assert r.status_code == 200

        # Save json response to variable
        data = r.json()

        # Check returned data matches input
        assert data["status"] == "pending"
        assert data["price_total"] == 25.00

# Transaction Update - Valid
def test_update_transaction():
    fake_transactions = [make_transaction("order-1")]

    def mock_load():
        return [t.copy() for t in fake_transactions]

    def mock_save(data):
        fake_transactions.clear()
        fake_transactions.extend(data)

    with patch("app.services.payments_service.transaction_repo.load_all", side_effect=mock_load), \
         patch("app.services.payments_service.transaction_repo.save_all", side_effect=mock_save):
        r = client.put("/payments/order-1", json={"price_total": 50.00})
        assert r.status_code == 200

        # Save json response to variable
        data = r.json()

        # Check returned data reflects the update
        assert data["price_total"] == 50.00

# Transaction Update - Not Found
def test_update_transaction_na():
    with patch("app.services.payments_service.transaction_repo.load_all", return_value=[]):
        r = client.put("/payments/nonexistent-order", json={"price_total": 50.00})
        assert r.status_code == 404

# Transaction Update - Invalid Price
def test_update_transaction_invalid_price():
    fake_transactions = [make_transaction("order-1")]

    with patch("app.services.payments_service.transaction_repo.load_all", return_value=fake_transactions):
        r = client.put("/payments/order-1", json={"price_total": -10.00})
        assert r.status_code == 422

# Transaction Update - Unauthorized
def test_update_transaction_unauthorized():
    # Switch to non-admin user
    def override_non_admin():
        return User(id="user-id", name="User", email="user@example.com", password="Password123!", role="user")
    app.dependency_overrides[get_current_user] = override_non_admin

    r = client.put("/payments/some-order", json={"price_total": 50.00})
    assert r.status_code == 403

# Transaction Update - Status Declined
def test_update_transaction_declined():
    fake_transactions = [make_transaction("order-1")]

    def mock_load():
        return [t.copy() for t in fake_transactions]

    def mock_save(data):
        fake_transactions.clear()
        fake_transactions.extend(data)

    with patch("app.services.payments_service.transaction_repo.load_all", side_effect=mock_load), \
         patch("app.services.payments_service.transaction_repo.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.OrdersService.update_order_status"):
        r = client.put("/payments/order-1", json={"status": "declined"})
        assert r.status_code == 200

        # Check returned data reflects the update
        data = r.json()
        assert data["status"] == "declined"

# Transaction Update - Status Approved
def test_update_transaction_approved():
    fake_transactions = [make_transaction("order-1")]

    def mock_load():
        return [t.copy() for t in fake_transactions]

    def mock_save(data):
        fake_transactions.clear()
        fake_transactions.extend(data)

    with patch("app.services.payments_service.transaction_repo.load_all", side_effect=mock_load), \
         patch("app.services.payments_service.transaction_repo.save_all", side_effect=mock_save), \
         patch("app.services.orders_service.OrdersService.update_order_status"):
        r = client.put("/payments/order-1", json={"status": "approved"})
        assert r.status_code == 200

        # Check returned data reflects the update
        data = r.json()
        assert data["status"] == "approved"

# Transaction Delete - Valid
def test_delete_transaction():
    fake_transactions = [make_transaction("order-1")]

    def mock_load():
        return [t.copy() for t in fake_transactions]

    def mock_save(data):
        fake_transactions.clear()
        fake_transactions.extend(data)

    with patch("app.services.payments_service.transaction_repo.load_all", side_effect=mock_load), \
         patch("app.services.payments_service.transaction_repo.save_all", side_effect=mock_save):
        r = client.delete("/payments/order-1")
        assert r.status_code == 204

# Transaction Delete - Not Found
def test_delete_transaction_na():
    with patch("app.services.payments_service.transaction_repo.load_all", return_value=[]):
        r = client.delete("/payments/order_na")
        assert r.status_code == 404

# Transaction Delete - Unauthorized
def test_delete_transaction_unauthorized():
    fake_transactions = [make_transaction("order-1", user_id="admin")]

    # Switch to non-admin user who does not own the transaction
    def override_non_admin():
        return User(id="user", name="User", email="user@example.com", password="Password123!", role="user")
    app.dependency_overrides[get_current_user] = override_non_admin

    with patch("app.services.payments_service.transaction_repo.load_all", return_value=[t.copy() for t in fake_transactions]):
        r = client.delete("/payments/order-1")
        assert r.status_code == 403

# Get Card For User - Valid
def test_get_card_for_user_valid():
    save_cards([{
        "id": "card-1",
        "user_id": "user-1",
        "card_num": "4868719196829038",
        "card_cvc": "344",
        "card_exp": "2029-11",
        "holder_name": "Test User",
        "holder_address": "123 Test St"
    }])

    card = fake_get_card("card-1", "user-1")

    # Check id matches and card details are returned unmasked
    assert card.id == "card-1"
    assert card.user_id == "user-1"

# Get Card For User - Not Found
def test_get_card_for_user_na():
    with pytest.raises(HTTPException) as e:
        fake_get_card("card-1", "user-1")
    assert e.value.status_code == 404

# Get Card For User - Unauthorized
def test_get_card_for_user_unauthorized():
    save_cards([{
        "id": "card-1",
        "user_id": "other-user",
        "card_num": "4868719196829038",
        "card_cvc": "344",
        "card_exp": "2029-11",
        "holder_name": "Other User",
        "holder_address": "456 Other St"
    }])

    with pytest.raises(HTTPException) as e:
        fake_get_card("card-1", "user-1")
    assert e.value.status_code == 403

# Create Transaction - Valid
def test_create_transaction_valid():
    save_cards([TEST_CARD_DATA])

    payment = PaymentTransaction(
        payment_id="pay-1",
        order_id="order-1",
        user_id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        card=CreditCard(**TEST_CARD_DATA),
        status=PaymentStatusType.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        price_total=25.00
    )

    result = fake_create_payment(payment)

    # Check returned status is pending
    assert result == PaymentStatusType.pending

# Create Transaction - Duplicate
def test_create_transaction_duplicate():
    save_cards([TEST_CARD_DATA])
    save_transactions([make_transaction("order-1")])

    payment = PaymentTransaction(
        payment_id="pay-1",
        order_id="order-1",
        user_id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        card=CreditCard(**TEST_CARD_DATA),
        status=PaymentStatusType.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        price_total=25.00
    )

    with pytest.raises(HTTPException) as e:
        fake_create_payment(payment)
    assert e.value.status_code == 409

# Create Transaction - Card Not Found
def test_create_transaction_card_na():
    payment = PaymentTransaction(
        payment_id="pay-1",
        order_id="order-1",
        user_id="8c6dbfcb-72c5-4cc4-9f76-29200f0ecda7",
        card=CreditCard(**TEST_CARD_DATA),
        status=PaymentStatusType.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        price_total=25.00
    )

    with pytest.raises(HTTPException) as e:
        fake_create_payment(payment)
    assert e.value.status_code == 404


# Card Update - All Fields Valid
def test_update_card_all_fields():
    card_id = create_test_card()
    r = client.put(
        f"/payments/cards/{card_id}",
        json={
            "card_num": "4111111111111111",
            "card_cvc": "321",
            "card_exp": "2030-06",
            "holder_address": "789 Updated Ave, Kelowna, BC"
        }
    )
    assert r.status_code == 200

    data = r.json()
    assert data["card_exp"] == "2030-06"
    assert data["holder_address"] == "789 Updated Ave, Kelowna, BC"
    assert data["card_cvc"] == "***"                                    # Check cvc is masked

# Transaction Update - Unauthorized
def test_update_transaction_unauthorized():
    save_transactions([make_transaction("order-1")])
    non_admin = User(id="user-id", name="User", email="user@example.com", password="Password123!", role="user")

    with pytest.raises(HTTPException) as e:
        fake_update_payment("order-1", non_admin, PaymentUpdate(price_total=10.0))
    assert e.value.status_code == 403

# Transaction Update - Declined Order Fail
def test_update_transaction_declined_order_fail():
    save_transactions([make_transaction("order-1")])

    with patch("app.services.orders_service.OrdersService.update_order_status",
               side_effect=HTTPException(status_code=404, detail="Order not found.")):
        r = client.put("/payments/order-1", json={"status": "declined"})
        assert r.status_code == 403
