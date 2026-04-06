import pytest
from datetime import datetime, timezone
from app.schemas.payment_method import CreditCard
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusType

# Mock payment method returned for user 
def _fake_get_card_for_user(card_id: str, user_id: str) -> CreditCard:
    return CreditCard(
        id=card_id,
        user_id=user_id,
        card_num="4111111111111111",
        card_cvc="123",
        card_exp="2030-01",
        holder_name="Test User",
        holder_address="1 Test St",
    )

# Mock payment transaction created 
def _fake_create_transaction(payment):
    return payment

# Mock payment pending transaction lookup
def _fake_get_transaction_by_id(order_id: str, user_id: str) -> PaymentTransaction:
    return PaymentTransaction(
        payment_id="test-transaction",
        order_id=order_id,
        user_id=user_id,
        card=CreditCard(
            id="fake-card",
            user_id=user_id,
            card_num="4111111111111111",
            card_cvc="123",
            card_exp="2030-01",
            holder_name="Test User",
            holder_address="1 Test St",
        ),
        status=PaymentStatusType.pending,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        price_total=0.0
    )

# Override function for payment method validation
@pytest.fixture(autouse=True)
def stub_payment_dependencies(monkeypatch):
    monkeypatch.setattr("app.services.orders_service.get_card_for_user", _fake_get_card_for_user)
    monkeypatch.setattr("app.services.payments_service.get_card_for_user", _fake_get_card_for_user)
    monkeypatch.setattr("app.services.orders_service.create_transaction", _fake_create_transaction)
    monkeypatch.setattr("app.services.payments_service.get_transaction_by_id", _fake_get_transaction_by_id)
    yield