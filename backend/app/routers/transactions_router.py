from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusResponse, PaymentUpdate
from app.schemas.user import User
from app.services.payments_service import get_transaction_by_id, update_transaction, delete_transaction
from app.auth.token_utils import get_current_user

router = APIRouter(prefix="/payments", tags=["Transactions"])

# # Get all user owned credit cards
# @router.get("", response_model=List[CreditCard])
# def get_my_cards(current_user: User = Depends(get_current_user)):
#     return list_user_cards(current_user.id)

# Get transaction by order_id
@router.get("/{order_id}", response_model=PaymentTransaction)
def get_transaction_by_order_id(order_id: str, current_user: User = Depends(get_current_user)):
    payment = get_transaction_by_id(order_id, current_user.id)
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction.")
    return payment

# Get transaction status by order_id
@router.get("/status/{order_id}", response_model=PaymentStatusResponse)
def get_payment_status_by_order_id(order_id: str, current_user: User = Depends(get_current_user)):
    payment = get_transaction_by_id(order_id, current_user.id)
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this transaction.")
    status = PaymentStatusResponse(
        card_num = str(payment.card.card_num),
        status = payment.status,
        updated_at = payment.updated_at,
        price_total = payment.price_total
    )
    return status

# Update transaction
@router.put("/{order_id}", response_model=PaymentTransaction)
def put_transaction(order_id: str, payload: PaymentUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction.")
    return update_transaction(order_id, current_user, payload)

# Delete transaction 
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_transaction(order_id: str, current_user: User = Depends(get_current_user)):
    delete_transaction(order_id, current_user)
    return None