"""
Feat4-SR1
The system shall allow users to create food orders

This file contains business logic for creating and retrieving orders.
Here, we can:
- Validate order contents
- Ensure an order has at least one item
- Delegate persistence/retrieval to the repository
"""
from app.schemas.order import OrderStatusUpdateRequest, CreateOrderResponse,DeliveryInfoUpdateRequest,Order,DeliveryInfoResponse
from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.order import CreateOrderResponse, CreateOrderRequest, Order, OrderItem
from app.schemas.delivery import DeliveryType, DeliveryStatus
from app.schemas.menu import MenuItem
from app.repositories.orders_repository import load_all, save_all
from typing import List, Dict
from datetime import datetime, timezone
from uuid import uuid4
from app.services.menu_service import fetch_menu_by_restaurant_id


class OrdersService:
    def list_orders(self):
        return [Order(**it) for it in load_all()]
    
    def create_order_tariq(self, order_request: CreateOrderRequest):
        # Load orders
        orders = load_all()

        # # This is the endpoint for creating an order. It generates a notification when an order is created. key endpoint for SR1. Updated in SR2 as it now stores in memory.
        # if order_request.delivery_method is not None:
        #     if order_request.delivery_method not in DeliveryType:
        #         raise HTTPException(status_code=400,detail="delivery_method must be either 'delivery' or 'pickup'.")

        #     if order_request.delivery_method == DeliveryType.delivery and not order_request.delivery_address:
        #         raise HTTPException(status_code=400,detail="delivery_address is required for delivery orders.")

        #     if order_request.delivery_method == DeliveryType.pickup and not order_request.pickup_location:
        #         raise HTTPException(status_code=400,detail="pickup_location is required for pickup orders.")

        order_id = str(uuid4())     #Generates a unique order ID using uuid4.
        timestamp = datetime.now(timezone.utc)     #records time for when order is created/updated/delivered
        
        new_order = CreateOrderResponse(
            order_id = order_id,
            user_id = order_request.user_id,
            restaurant_id = order_request.restaurant_id,
            items = order_request.items,
            status = DeliveryStatus.created,
            delivery_method= DeliveryType(order_request.delivery_method),
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
        menu = fetch_menu_by_restaurant_id(restaurant_id)

        valid_menu_ids = {item.menuItemId for item in menu}
        for order_item in items:
            if order_item.menuItemId not in valid_menu_ids:
                raise ValueError(f"Invalid menuItemId: {order_item['menuItemId']} for restaurant {restaurant_id}")

        return None #repo.create_order(restaurant_id, items)

    def get_order_by_id(self, order_id):
        # Retrieve the order from the repository
        orders = load_all()

        # Iterate through orders list
        for it in orders:
            # Return the found order
            if str(it.get("order_id")) == order_id:
                return CreateOrderResponse(**it)  
        raise HTTPException(status_code=404, detail="Order not found.") # Quick error handling for not found

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


     # Update Order Delivery Status
    def assign_delivery_info(self, order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
        orders = load_all()
        
        for idx, order in enumerate(orders):
            if str(order.get("order_id")) == order_id:
                # Set new values
                if delivery_request.delivery_method is not None:
                    order["delivery_method"] = delivery_request.delivery_method
                if delivery_request.delivery_address is not None:
                    order["delivery_address"] = delivery_request.delivery_address
                if delivery_request.pickup_location is not None:
                    order["pickup_location"] = delivery_request.pickup_location
                order["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") # Convert to a string to prevent json save issues

                # Set order entry with updated values
                orders[idx] = order

                # Save changes to order
                save_all(orders)
                return CreateOrderResponse(**order)
        raise HTTPException(status_code=404, detail="Order not found.")

    # Update Order Information
    def update_order_info(self, update_order_id: str, items: List[OrderItem], restaurant_id: str):
        orders_store = load_all()
        
        # Search order list for order associated with update_order_id
        for idx, o in enumerate(orders_store):
            # Check if update_restaurant_id matches
            if str(o.get("order_id")) == str(update_order_id):
                if o.get("status") in (DeliveryStatus.delivered, DeliveryStatus.picked_up):
                    raise HTTPException(status_code=400, detail="Cannot update a completed (Delivered or Picked up) order.")
                if restaurant_id is not None:
                    o["restaurant_id"] = restaurant_id
                if items is not None:
                    o["items"] = [it.model_dump() for it in items]
                o["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                
                # Save changes to orders list
                orders_store[idx] = o
                save_all(orders_store)

                # Return order
                return Order(**o)
        # Throw exception if order does not exist
        raise HTTPException(status_code=404,detail=f"Order not found.")

    # def assign_delivery_info(self, order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> CreateOrderResponse:
    #     if order_id not in orders_store:
    #         raise HTTPException(status_code=404, detail="Order not found.")

    #     order = orders_store[order_id]

    #     order.delivery_method = delivery_request.delivery_method
    #     order.delivery_address = delivery_request.delivery_address
    #     order.pickup_location = delivery_request.pickup_location
    #     order.updated_at = datetime.now(timezone.utc)

    #     orders_store[order_id] = order
    #     return order