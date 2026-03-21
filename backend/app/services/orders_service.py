"""
Feat4-SR1
The system shall allow users to create food orders

This file contains business logic for creating and retrieving orders.
Here, we can:
- Validate order contents
- Ensure an order has at least one item
- Delegate persistence/retrieval to the repository
"""
from app.schemas.order import OrderStatusUpdateRequest, CreateOrderResponse
from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.order import CreateOrderResponse, CreateOrderRequest
from app.repositories.orders_repository import save_all, load_all
from typing import List, Dict
from datetime import datetime, timezone
from uuid import uuid4
DELIVERY_STATUS_TRANSITIONS = {
                #"Created": ["Preparing"],
                #"Preparing": ["Ready"],
                #"Ready": []
            "Created": ["Preparing"],
            "Preparing": ["Ready"],
            "Ready": ["Delivered"],
            "Delivered": []
            }

PICKUP_STATUS_TRANSITIONS = {
            # "Created": ["Preparing"],
                #"Preparing": ["Ready"],
            # "Ready": []
                "Created": ["Preparing"],
                "Preparing": ["Ready"],
                "Ready": ["Picked up"],
                "Picked up": []
            }

class OrdersService:
    def __init__(self, repo, restaurants_repo):
        self.repo = repo
        self.restaurants_repo = restaurants_repo

    # 
    def create_order_tariq(self, order_request: CreateOrderRequest) -> CreateOrderResponse:
        # Load orders
        orders = load_all()

        # This is the endpoint for creating an order. It generates a notification when an order is created. key endpoint for SR1. Updated in SR2 as it now stores in memory.
        if order_request.delivery_method is not None:
            if order_request.delivery_method not in ["delivery", "pickup"]:
                raise HTTPException(status_code=400,detail="delivery_method must be either 'delivery' or 'pickup'.")

            if order_request.delivery_method == "delivery" and not order_request.delivery_address:
                raise HTTPException(status_code=400,detail="delivery_address is required for delivery orders.")

            if order_request.delivery_method == "pickup" and not order_request.pickup_location:
                raise HTTPException(status_code=400,detail="pickup_location is required for pickup orders.")

        order_id = str(uuid4())     #Generates a unique order ID using uuid4.
        timestamp = datetime.now(timezone.utc)     #records time for when order is created/updated/delivered
        
        new_order = CreateOrderResponse(
            order_id = order_id,
            user_id = order_request.user_id,
            restaurant_id = order_request.restaurant_id,
            items = order_request.items,
            status = "Created",
            delivery_method=order_request.delivery_method,
            delivery_address=order_request.delivery_address,
            pickup_location=order_request.pickup_location,
            created_at = timestamp,
            updated_at = timestamp,
            delivered_at = None
        )

        orders.append(new_order.model_dump(mode='json'))
        save_all(orders)
    
        #Generate a notification for the order creation event.
        #notification.create_order_created_notification(user_id = order_request.user_id, order_id = order.order_id)

        return new_order

    def create_order(self, restaurant_id, items):
        # Order must contain at least one item
        if not items or len(items) == 0:
            raise ValueError("Order must contain at least one item")

        # Validate menuItemIds against restaurant's menuItems
        restaurants = self.restaurants_repo.get_all()
        restaurant = next((r for r in restaurants if r["restaurant_id"] == restaurant_id), None)
        if not restaurant:
            raise ValueError("Restaurant not found")

        valid_menu_ids = {item["menuItemId"] for item in restaurant["menuItems"]}
        for order_item in items:
            if order_item["menuItemId"] not in valid_menu_ids:
                raise ValueError(f"Invalid menuItemId: {order_item['menuItemId']} for restaurant {restaurant_id}")

        return self.repo.create_order(restaurant_id, items)

    def get_order_by_id(self, order_id):
        # Retrieve the order from the repository
        order = self.repo.get_order_by_id(order_id)

        if order is None:
            raise ValueError("Order not found") # Quick error handling for not found

        return order # Return the found order
    



    def update_order_status(self, order_id: str, status_request: OrderStatusUpdateRequest) -> CreateOrderResponse:
        orders_store = load_all()
        #this updated status of existing order and generates a notif when status changes. Essential for SR2.
        if order_id not in orders_store:
            raise HTTPException(status_code = 404, detail = "Order not found.")     #404 - not found if order ID does not exist in the in-memory store.
        
        order = orders_store[order_id]
        
        old_status = order.status
        new_status = status_request.status
        
        if old_status == new_status:
            raise HTTPException(status_code = 400, detail = "Order status remains unchanged.")  

        if order.delivery_method == "pickup":
            allowed_next_statuses = PICKUP_STATUS_TRANSITIONS.get(old_status, [])
        else:
            allowed_next_statuses = DELIVERY_STATUS_TRANSITIONS.get(old_status, [])

        if new_status not in allowed_next_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status transition from '{old_status}' to '{new_status}'.")

        
        timestamp = datetime.now(timezone.utc)
        
        order.status = new_status     #Update the order status in the in-memory store.
        order.updated_at = timestamp
        
        if new_status =="Delivered":
            order.delivered_at = timestamp
            
        orders_store[order_id] = order     #Save the updated order back to the in-memory store.
        
            
        #Now generate a notification for the order status change event.
        notification.create_order_status_changed_notification(
            user_id = order.user_id,
            order_id = order.order_id,
            old_status = old_status,
            new_status = new_status
        )
        
        return order