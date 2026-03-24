from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.payment_method import CreditCard, CreditCardCreate
from app.schemas.user import User
from app.services.payments_service import get_card_by_id, create_card, delete_card
from app.auth.token_utils import get_current_user

router = APIRouter(prefix="/payments/cards", tags=["Payment Methods"])

# Get credit card by id
@router.get("/{card_id}", response_model=CreditCard)
def get_card(card_id: str, current_user: User = Depends(get_current_user)):
    card = get_card_by_id(card_id)
    if card.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this card.")
    return card

# Create credit card
@router.post("", response_model=CreditCard, status_code=201)
def add_card(payload: CreditCardCreate, current_user: User = Depends(get_current_user)):
    return create_card(current_user.id, payload)

# Delete credit card 
@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(card_id: str, current_user: User = Depends(get_current_user)):
    delete_card(card_id, current_user)
    return None

