import uuid
from typing import List
from fastapi import HTTPException
from app.schemas.payment_method import CreditCard, CreditCardCreate
from app.schemas.user import User
from app.repositories.payment_methods_repository import load_all, save_all
from app.schemas.card_validator import CardValidator

def list_user_cards(user_id: str) -> List[CreditCard]:
    """
    Returns all cards belonging to a specific user
    """
    # Load card list
    cards = load_all()
    user_cards = []

    # Fetch cards that are owned by the userid
    for c in cards:
        # If card is owned by user then mask details and add it to return list
        if c.get("user_id") == user_id:   
            # Retrieve Card
            card = CreditCard(**c)

            # Mask Details
            card.card_num = "*"*(len(card.card_num)-4) + card.card_num[len(card.card_num)-4:] # Mask card number and show only last 4 digits
            card.card_cvc = "***" # Mask cvc

            # Add card to return list
            user_cards.append(card)
    # Return list of cards to user
    return user_cards


def create_card(user_id: str, payload: CreditCardCreate) -> CreditCard:
    """
    Creates a new card for a user
    Raises 422 if any input is invalid
    Raises 409 if random uuid(card_id) is already used in the system
    """
    # Load card list
    cards = load_all()

    # Fetch card values
    new_card_id = str(uuid.uuid4())
    new_card_num = payload.card_num.strip()
    new_card_cvc=payload.card_cvc.strip()
    new_card_exp=payload.card_exp.strip()
    new_holder_name=payload.holder_name.strip()
    new_holder_adr=payload.holder_address.strip()

    # Card input validation
    if not CardValidator.is_valid_card_num(new_card_num):
        raise HTTPException(status_code=422, detail="Invalid Card Number. Must be numbers 0-9 and 13-19 digits long.")
    if not CardValidator.is_valid_cvc(new_card_cvc):
        raise HTTPException(status_code=422, detail="Invalid CVC. Must be numbers 0-9 and 3-4 digits long.")
    if not CardValidator.is_valid_expiry(new_card_exp):
        raise HTTPException(status_code=422, detail="Invalid Expiry Date. Must be numbers 0-9 and formatted YYYY-MM.")
    if not CardValidator.is_valid_name(new_holder_name):
        raise HTTPException(status_code=422, detail="Invalid Name. Card holder name cannot contain special characters.")
    if not CardValidator.is_valid_address(new_holder_adr):
        raise HTTPException(status_code=422, detail="Invalid Address. Billing address can only contain letters, numbers, spaces, '-', or ','.")

    # Card_id conflict validation
    if any(it.get("id") == new_card_id for it in cards): 
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    
    # Create card
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
    """
    Returns the card matching the card_id
    Raises 404 if no card exists
    """
    # Load card list
    cards = load_all()
    
    # Fetch card associated with card_id
    for c in cards:
        if c.get("id") == card_id:
            # Retrieve Card
            card = CreditCard(**c)

            # Mask Details
            card.card_num = "*"*(len(card.card_num)-4) + card.card_num[len(card.card_num)-4:] # Mask card number and show only last 4 digits
            card.card_cvc = "***" # Mask cvc

            # Return Card
            return card
    raise HTTPException(status_code=404, detail="Credit Card {card_id} not found.")

def delete_card(card_id: str, current_user: User) -> None:
    """
    Deletes the card matching the given card_id
    Raises 403 if user not authorized to delete this card
    Raises 404 if no card exists
    """
    # Load card list
    cards = load_all()
    new_cards = []

    # Search card list
    for c in cards:
        # Check card is associated with card_id
        if c.get("id") != card_id:
            new_cards.append(c)
        # Check user is authorized to remove card
        elif c.get("id") == card_id:
            if c.get("user_id") != current_user.id or current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to delete this card.")

    # Check if new card list does not contain card        
    if len(new_cards) == len(cards):
        raise HTTPException(status_code=404, detail="Credit card not found.")
    
    # Save new card list
    new_cards = [c for c in cards if c.get("id") != card_id]
    save_all(new_cards)