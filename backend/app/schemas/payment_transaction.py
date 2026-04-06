from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum
from app.schemas.payment_method import CreditCard

# Payment Status 
class PaymentStatusType (StrEnum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    refunded = "refunded"

# Payment Details
class PaymentTransaction(BaseModel):
    payment_id: str
    order_id: str
    user_id: str
    card: CreditCard
    status: PaymentStatusType = PaymentStatusType.pending
    created_at: datetime
    updated_at: datetime
    price_total: float

# Payment Status Details
class PaymentStatusResponse(BaseModel):
    card_num: str
    status: PaymentStatusType
    updated_at: datetime
    price_total: float

# Payment Update Details
class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatusType] = None
    price_total: Optional[float] = None