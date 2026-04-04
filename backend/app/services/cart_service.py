from typing import Dict, Any, Optional
from app.repositories.cart_repository import load_all, save_all


def get_cart_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    carts = load_all()
    for cart in carts:
        if cart.get('user_id') == user_id:
            return cart
    return None


def save_cart(cart: Dict[str, Any]):
    carts = load_all()
    for idx, c in enumerate(carts):
        if c.get('user_id') == cart.get('user_id'):
            carts[idx] = cart
            break
    else:
        carts.append(cart)
    save_all(carts)


def delete_cart_by_user_id(user_id: str):
    carts = load_all()
    carts = [c for c in carts if c.get('user_id') != user_id]
    save_all(carts)
