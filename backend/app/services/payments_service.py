import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.payment_method import CreditCard, CreditCardCreate
from app.repositories.payment_methods_repository import load_all, save_all

def create_card(user_id: str, payload: CreditCardCreate) -> CreditCard:
    """Creates a new card for a user"""
    # Load card list
    cards = load_all()

    # Fetch card values
    new_card_id = str(uuid.uuid4())
    new_card_num = payload.card_num.strip()
    new_card_cvc=payload.card_cvc.strip()
    new_card_exp=payload.card_exp.strip()
    new_holder_name=payload.holder_name.strip()
    new_holder_adr=payload.holder_address.strip()

    # Create Card
    new_card = CreditCard(
        id=new_card_id,
        user_id=user_id,
        card_num=new_card_num,
        card_cvc=new_card_cvc,
        card_exp=new_card_exp,
        holder_name=new_holder_name,
        holder_address=new_holder_adr
    )
    
    # Save card and return result
    cards.append(new_card.model_dump(mode='json'))
    save_all(cards)
    return new_card

def get_card_by_id(card_id: str) -> CreditCard:
    """Returns the card matching the card_id"""
    # Load card list
    cards = load_all()
    
    # Fetch card associated with card_id
    for c in cards:
        if c.get("id") == card_id:
            # Retrieve Card
            card = CreditCard(**c)

            # Return Card
            return card
    raise HTTPException(status_code=404, detail="Credit card not found.")
