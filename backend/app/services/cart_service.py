from fastapi import HTTPException
from app.services.menu_service import fetch_menu_by_restaurant_id
from app.schemas.cart import CartCheckoutRequest, UpdateCartItemRequest
from typing import Dict, Any, Optional
from app.repositories.cart_repository import load_all, save_all
from app.schemas.order import OrderItem, CreateOrderRequest, CreateOrderResponse
from app.services.orders_service import OrdersService

"""
Cart will take ideas from Orders, but
work more with the idea that each user only gets one active cart
ie cart is tied directly to user id
"""

def get_cart_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    carts = load_all()
    for cart in carts:
        if cart.get('user_id') == user_id:
            return cart
    return None

# Save cart: if cart for user exists, update it, otherwise add new cart
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


def add_item_to_cart(user_id: str, restaurant_id: str, menu_item_id: int, quantity: int):
    """
    Add a valid menu item to the user's cart. If the cart does not exist, create it.
    Validates menu item and restaurant. Raises HTTPException if invalid.
    """
    # Validate menu item
    menu_items = fetch_menu_by_restaurant_id(restaurant_id)
    menu_item = next((item for item in menu_items if item.menuItemId == menu_item_id), None)
    # We can stay consistent with Orders by only taking valid menu items, and having quantity > 1
    if not menu_item:
        raise HTTPException(status_code=400, detail=f"Invalid menuItemId: {menu_item_id} for restaurant {restaurant_id}.")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1.")

    cart = get_cart_by_user_id(user_id)
    now = __import__('datetime').datetime.now()
    if cart:
        # If cart is for a different restaurant, reset it
        # This is a design choice: a cart can only contain items from one restaurant
        # Our project has serious time constraints, and this does not contradict anything specified on the feature
        if cart["restaurant_id"] != restaurant_id:
            cart = {
                "user_id": user_id,
                "restaurant_id": restaurant_id,
                "items": [],
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }
        # Check if item already in cart, if it is, just add quantity
        # For now, just add to quantity** I will worry about SR2 later
        for item in cart["items"]:
            if item["menuItemId"] == menu_item_id:
                item["quantity"] += quantity
                cart["updated_at"] = now.isoformat()
                save_cart(cart)
                return cart
        # Add new item if it's not already in cart
        cart["items"].append({
            "menuItemId": menu_item.menuItemId,
            "name": menu_item.name,
            "price": menu_item.price,
            "quantity": quantity
        })
        cart["updated_at"] = now.isoformat()
        save_cart(cart)
        return cart
    else:
        # If cart does not exist, create new cart
        cart = {
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "items": [{
                "menuItemId": menu_item.menuItemId,
                "name": menu_item.name,
                "price": menu_item.price,
                "quantity": quantity
            }],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        save_cart(cart)
        return cart


# Checkout logic: converts cart to order, calls order service, clears cart
# The idea is to link cart and orders by user_id, and restaurant_id
def checkout_cart(request: CartCheckoutRequest) -> CreateOrderResponse:
    cart = get_cart_by_user_id(request.user_id)
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty or does not exist.")

    # Convert cart items to order items
    order_items = [
        OrderItem(
            menuItemId=item["menuItemId"],
            name=item["name"],
            price=item["price"],
            quantity=item["quantity"]
        ) for item in cart["items"]
    ]

    order_request = CreateOrderRequest(
        user_id=request.user_id,
        card_id=request.card_id,
        restaurant_id=cart["restaurant_id"],
        items=order_items,
        delivery_method=request.delivery_method,
        delivery_address=request.delivery_address,
        pickup_location=request.pickup_location
    )

    # Create order
    orders_service = OrdersService()
    order = orders_service.create_order(order_request)

    # Clear cart
    delete_cart_by_user_id(request.user_id)

    return order

def update_cart_item(request: UpdateCartItemRequest):
    cart = get_cart_by_user_id(request.user_id)
    if not cart or cart["restaurant_id"] != request.restaurant_id:
        raise HTTPException(status_code=404, detail="Cart not found for user and restaurant.")
    found = False
    for item in cart["items"]:
        if item["menuItemId"] == request.menu_item_id:
            found = True
            if request.quantity == 0:
                cart["items"].remove(item)
            else:
                item["quantity"] = request.quantity
            break
    if not found:
        raise HTTPException(status_code=404, detail="Item not found in cart.")
    cart["updated_at"] = __import__('datetime').datetime.now().isoformat()
    save_cart(cart)
    return cart

