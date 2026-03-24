from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.payment_method import CreditCard, CreditCardCreate

router = APIRouter(prefix="/payments/cards", tags=["Payment Methods"])
