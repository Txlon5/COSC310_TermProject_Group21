from pydantic import BaseModel
from typing import Optional

# Credit Card
class CreditCard(BaseModel):
    id: str
    user_id: str
    card_num: str
    card_cvc: str
    card_exp: str
    holder_name: str
    holder_address: str

# Credit Card - Create Class  
class CreditCardCreate(BaseModel):
    card_num: str
    card_cvc: str
    card_exp: str
    holder_name: str
    holder_address: str

# Credit Card - Update Class  
class CreditCardUpdate(BaseModel):
    card_num: Optional[str] = None
    card_cvc: Optional[str] = None
    card_exp: Optional[str] = None
    holder_name: Optional[str] = None
    holder_address: Optional[str] = None