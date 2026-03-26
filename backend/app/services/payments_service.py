import uuid
import random
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.schemas.payment_method import CreditCard, CreditCardCreate, CreditCardUpdate
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusType, PaymentUpdate
from app.schemas.order import OrderStatusUpdateRequest
from app.schemas.delivery import DeliveryStatus
from app.schemas.user import User
from app.repositories import payment_methods_repository as card_repo
from app.repositories import transactions_repository as transaction_repo
from app.schemas.card_validator import CardValidator

# [Payment Method Functions]
def list_user_cards(user_id: str) -> List[CreditCard]:
    """
    Returns all cards belonging to a specific user
    """
    # Load card list
    cards = card_repo.load_all()
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
    cards = card_repo.load_all()

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
    card_repo.save_all(cards)
    return new_card

def get_card_by_id(card_id: str) -> CreditCard:
    """
    Returns the card matching the card_id with masked details
    Raises 404 if no card exists
    """
    # Load card list
    cards = card_repo.load_all()
    
    # Search card list
    for c in cards:
        # Check if card_id matches
        if str(c.get("id")) == card_id:
            # Retrieve Card
            card = CreditCard(**c)

            # Mask Details
            card.card_num = "*"*(len(card.card_num)-4) + card.card_num[len(card.card_num)-4:] # Mask card number and show only last 4 digits
            card.card_cvc = "***" # Mask cvc

            # Return Card
            return card
    raise HTTPException(status_code=404, detail=f"Credit Card '{card_id}' not found.")

def get_card_for_user(card_id: str, user_id: str) -> CreditCard:
    """
    Returns the card details matching card_id if it belongs to the user 
    Raises 403 if user not authorized to use this card
    Raises 404 if no card exists
    """
    # Load card list
    cards = card_repo.load_all()
    # Search card list
    for c in cards:
        # Check if card_id matches
        if str(c.get("id")) == str(card_id):
            if str(c.get("user_id")) != str(user_id):
                raise HTTPException(status_code=403, detail="Not authorized to use this card.")
            return CreditCard(**c)

    raise HTTPException(status_code=404, detail=f"Credit card '{card_id}' not found.")

def update_card(card_id: str, current_user: User, payload: CreditCardUpdate) -> CreditCard:
    """
    Updates card details if it belongs to the user
    Raises 403 if user not authorized to update this card
    Raises 422 if any input is invalid
    Raises 404 if no card exists
    """
    cards = card_repo.load_all()
    
    # Search card list
    for idx, c in enumerate(cards):
        # Check if card_id matches
        if str(c.get("id")) == str(card_id):
            # Check if user owns the card
            if c.get("user_id") != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to update this card.")

            # Update fields if entered
            if payload.card_num is not None and payload.card_num.strip() != "":
                # Validate new card number
                if not CardValidator.is_valid_card_num(payload.card_num.strip()):
                    raise HTTPException(status_code=422, detail="Invalid card number. Must be 13-19 digits.")
                c["card_num"] = payload.card_num.strip()

            if payload.card_cvc is not None and payload.card_cvc.strip() != "":
                # Validate new cvc
                if not CardValidator.is_valid_cvc(payload.card_cvc.strip()):
                    raise HTTPException(status_code=422, detail="Invalid CVC. Must be 3 or 4 digits.")
                c["card_cvc"] = payload.card_cvc.strip()

            if payload.card_exp is not None and payload.card_exp.strip() != "":
                # Validate new expiry date
                if not CardValidator.is_valid_expiry(payload.card_exp.strip()):
                    raise HTTPException(status_code=422, detail="Invalid expiry format. Use YYYY-MM.")
                c["card_exp"] = payload.card_exp.strip()

            if payload.holder_name is not None and payload.holder_name.strip() != "":
                # Validate new card holder name
                if not CardValidator.is_valid_name(payload.holder_name.strip()):
                    raise HTTPException(status_code=422, detail="Holder name cannot contain special characters.")
                c["holder_name"] = payload.holder_name.strip()

            if payload.holder_address is not None and payload.holder_address.strip() != "":
                # Validate new card holder address
                if not CardValidator.is_valid_address(payload.holder_address.strip()):
                    raise HTTPException(status_code=422, detail="Address can only contain letters, numbers, spaces, '-', or ','.")
                c["holder_address"] = payload.holder_address.strip()

            # Save changes to card list
            cards[idx] = c
            card_repo.save_all(cards)

            # Retrieve card for masking
            card = CreditCard(**c)

            # Mask details before returning
            card.card_num = "*"*(len(card.card_num)-4) + card.card_num[-4:] 
            card.card_cvc = "***" 

            # Return card
            return card
    # Throw exception if card does not exist
    raise HTTPException(status_code=404, detail=f"Credit card '{card_id}' not found")

def delete_card(card_id: str, current_user: User) -> None:
    """
    Deletes the card matching the given card_id
    Raises 403 if user not authorized to delete this card
    Raises 404 if no card exists
    """
    # Load card list
    cards = card_repo.load_all()
    new_cards = []

    # Search card list
    for c in cards:
        # Check card is associated with card_id
        if str(c.get("id")) != card_id:
            new_cards.append(c)
        # Check user is authorized to remove card
        elif str(c.get("id")) == card_id:
            if str(c.get("user_id")) != str(current_user.id) and str(current_user.role) != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to delete this card.")

    # Check if new card list does not contain card        
    if len(new_cards) == len(cards):
        raise HTTPException(status_code=404, detail="Credit card not found.")
    
    # Save new card list
    card_repo.save_all(new_cards)

# [Payment Transaction Functions]

def get_transaction_by_id(order_id: str, user_id: str) -> PaymentTransaction:
    """
    Returns the card details matching card_id if it belongs to the user 
    Raises 403 if user not authorized to use this card
    Raises 404 if no card exists
    """
    # Load transaction list
    payments = transaction_repo.load_all()
    
    # Search transaction list
    for t in payments:
        # Check if order_id matches
        if str(t.get("order_id")) == str(order_id):
            if str(t.get("user_id")) != str(user_id):
                raise HTTPException(status_code=403, detail="Not authorized to view this transaction.")
            # Mask Details
            transaction = PaymentTransaction(**t)
            # Get card number and mask details before returning to user
            mask_card_num = transaction.card.card_num 
            transaction.card.card_num = "*"*(len(mask_card_num)-4) + mask_card_num[len(mask_card_num)-4:] # Mask card number and show only last 4 digits
            transaction.card.card_cvc = "***" # Mask cvc
            # Return transaction to user
            return transaction
    # Throw exception if card does not exist
    raise HTTPException(status_code=404, detail=f"Payment Transaction for '{order_id}' not found.")


def create_transaction(payment: PaymentTransaction) -> PaymentStatusType:
    # Load transaction list
    payments = transaction_repo.load_all()
    cards = card_repo.load_all()

    # Collision check transaction list 
    for t in payments:
        # Check if transaction already exists
        if str(t.get("order_id")) == str(payment.order_id):
            raise HTTPException(status_code=409, detail="Transaction already exists.")
    
    # Card Validation
    for c in cards:
        # Check if transaction already exists
        if str(c.get("id")) == str(payment.card.id):
            # Save transaction and return result
            payments.append(payment.model_dump(mode='json'))
            transaction_repo.save_all(payments)
            # Return transaction status
            return payment.status
    # Throw exception if card does not exist
    raise HTTPException(status_code=404, detail=f"Credit card '{payment.card.id}' not found.")

def update_transaction(order_id: str, current_user: User, payload: PaymentUpdate) -> PaymentTransaction:
    """
    Updates transaction details if it belongs to the user
    Raises 403 if user not authorized to update this transaction
    Raises 422 if any input is invalid
    Raises 404 if no transaction exists
    """
    payments = transaction_repo.load_all()
    
    # Search transaction list
    for idx, t in enumerate(payments):
        # Check if order_id matches
        if str(t.get("order_id")) == str(order_id):
            # Check if user is admin
            if str(current_user.role) != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to update this transaction.")

            # Validate inputs
            if payload.price_total is not None and payload.price_total < 0:
                raise HTTPException(status_code=422, detail="Invalid price_total. Must be 0 or greater.")

            # Update fields
            t["status"] = payload.status
            t["price_total"] = payload.price_total
            t["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Import OrderService to update order status
            from app.services.orders_service import OrdersService


            # Adjust order status based on declined or approved status
            if (payload.status == PaymentStatusType.declined):
                # Order cancelled
                try:
                    # Import OrderService to update order status
                    order = OrdersService()
                    order.update_order_status(order_id, OrderStatusUpdateRequest(status=DeliveryStatus.cancelled))
                    print("CANCELLED")
                except HTTPException:
                    raise HTTPException(status_code=403, detail="Unable to update order status to cancelled.")  
            elif (payload.status == PaymentStatusType.approved):
                # Order ready
                try:
                    # Import OrderService to update order status
                    order = OrdersService()
                    order.update_order_status(order_id, OrderStatusUpdateRequest(status=DeliveryStatus.ready))
                    print("Approved")
                except HTTPException:
                    raise HTTPException(status_code=403, detail="Unable to update order status to approved.")  

            # Save changes
            payments[idx] = t
            transaction_repo.save_all(payments)

            # Make response transaction with masked card details
            transaction = PaymentTransaction(**t)
            mask_card_num = transaction.card.card_num
            transaction.card.card_num = "*" * (len(mask_card_num) - 4) + mask_card_num[-4:]
            transaction.card.card_cvc = "***"

            # Return updated transaction
            return transaction 
    # Throw exception if card does not exist
    raise HTTPException(status_code=404, detail=f"Transaction '{order_id}' not found")

def delete_transaction(order_id: str, current_user: User) -> None:
    """
    Deletes the transaction matching the given order_id
    Raises 403 if user not authorized to delete this transaction
    Raises 404 if no transaction exists
    """
    # Load transaction list
    payments = transaction_repo.load_all()
    new_payments = []

    # Search transaction list
    for t in payments:
        # Check order_id matches
        if str(t.get("order_id")) != order_id:
            new_payments.append(t)
        # Remove transaction from list
        elif str(t.get("order_id")) == order_id:
            # Check user is authorized to remove transaction
            if str(t.get("user_id")) != str(current_user.id) and str(current_user.role) != "admin":
                raise HTTPException(status_code=403, detail="Not authorized to delete this transaction.")

    # Check if new transaction list does not contain transaction        
    if len(new_payments) == len(payments):
        raise HTTPException(status_code=404, detail="Transaction not found.")
    
    # Save new transaction list
    new_payments = [t for t in payments if t.get("order_id") != order_id]
    transaction_repo.save_all(new_payments)