from fastapi import APIRouter, status, HTTPException
from app.services.cart_service import add_item_to_cart, get_cart_by_user_id, checkout_cart, update_cart_item
from app.schemas.cart import Cart, CartCheckoutRequest, AddCartItemRequest, UpdateCartItemRequest
from app.schemas.order import CreateOrderResponse
from typing import Optional
from pydantic import ValidationError


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add-item", response_model=Cart, status_code=status.HTTP_200_OK)
def add_item(request: AddCartItemRequest):
    cart = add_item_to_cart(
        user_id=request.user_id,
        restaurant_id=request.restaurant_id,
        menu_item_id=request.menu_item_id,
        quantity=request.quantity
    )
    return cart

@router.get("/get", response_model=Optional[Cart])
def get_cart(user_id: str):
    return get_cart_by_user_id(user_id)


@router.post("/checkout", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(request: CartCheckoutRequest):
    try:
        return checkout_cart(request)
    except ValidationError as e:
        detail = e.errors()
        raise HTTPException(status_code=400, detail=detail)

@router.post("/update-item", response_model=Cart, status_code=status.HTTP_200_OK)
def update_item(request: UpdateCartItemRequest):
    return update_cart_item(request)
