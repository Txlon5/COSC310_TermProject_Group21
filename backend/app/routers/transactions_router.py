from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusResponse
from app.schemas.user import User
from app.services.payments_service import get_transaction_by_id
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
        raise HTTPException(status_code=403, detail="Not authorized to view this card.")
    return payment

# Get transaction status by order_id
@router.get("/status/{order_id}", response_model=PaymentStatusResponse)
def get_payment_status_by_order_id(order_id: str, current_user: User = Depends(get_current_user)):
    payment = get_transaction_by_id(order_id, current_user.id)
    if payment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this card.")
    status = PaymentStatusResponse(
        card_num = str(payment.card.card_num),
        status = payment.status,
        updated_at = payment.updated_at,
        price_total = payment.price_total
    )
    return status


# # Update credit card
# @router.put("/{card_id}", response_model=CreditCard)
# def put_card(card_id: str, payload: CreditCardUpdate, current_user: User = Depends(get_current_user)):
#     return update_card(card_id, current_user, payload)

# # Create credit card
# @router.post("", response_model=CreditCard, status_code=201)
# def add_card(payload: CreditCardCreate, current_user: User = Depends(get_current_user)):
#     return create_card(current_user.id, payload)



# # Delete credit card 
# @router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
# def remove_card(card_id: str, current_user: User = Depends(get_current_user)):
#     delete_card(card_id, current_user)
#     return None

