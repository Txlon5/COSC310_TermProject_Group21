from app.schemas.order import OrderStatusUpdateRequest, CreateOrderResponse,DeliveryInfoUpdateRequest,Order, CreateOrderRequest, OrderItem, ReorderRequest
from fastapi import HTTPException
from app.schemas.order import CreateOrderResponse, CreateOrderRequest, Order, OrderItem
from app.schemas.payment_transaction import PaymentTransaction, PaymentStatusType
from app.schemas.delivery import DeliveryType, DeliveryStatus
from app.schemas.user import User
from app.services.notification_service import NotificationService
from app.repositories.orders_repository import load_all, save_all
from typing import List
from datetime import datetime, timezone
from app.services.payments_service import create_transaction, get_card_for_user
from uuid import uuid4
from app.services.menu_service import fetch_menu_by_restaurant_id

# Order Status Dictionary
PICKUP_STATUS_TRANSITIONS = {
    DeliveryStatus.created.value: [DeliveryStatus.preparing.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.preparing.value: [DeliveryStatus.ready.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.ready.value: [DeliveryStatus.picked_up.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.picked_up.value: [DeliveryStatus.complete.value]
}
DELIVERY_STATUS_TRANSITIONS = {
    DeliveryStatus.created.value: [DeliveryStatus.preparing.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.preparing.value: [DeliveryStatus.ready.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.ready.value: [DeliveryStatus.delivered.value, DeliveryStatus.cancelled.value],
    DeliveryStatus.delivered.value: [DeliveryStatus.complete.value]
}

class OrdersService:
    def __init__(self):
        self.notification = NotificationService()     #Creates an instance of NotificationService class. This will be used to generate notifications when orders are created.

    def list_orders(self):
        return [Order(**it) for it in load_all()]
    
    # Tariq/Siam [Notification]
    def create_order(self, order_request: CreateOrderRequest) -> CreateOrderResponse:
        # Order must contain at least one item
        if not order_request.items or len(order_request.items) == 0:
            raise ValueError("Order must contain at least one item")

        # Validate menuItemIds against restaurant's menuItems
        menu = fetch_menu_by_restaurant_id(order_request.restaurant_id)
        valid_menu_ids = {item.menuItemId for item in menu}
        
        restaurant_name = str(order_request.restaurant_id)

        # Check for at least one valid menu item with quantity >= 1
        has_valid_quantity = False
        total_price = 0.0
        for order_item in order_request.items:
            if order_item.menuItemId not in valid_menu_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid menuItemId: {order_item.menuItemId} for restaurant {order_request.restaurant_id}. Please check the menu items for this restaurant and use a valid menuItemId."
                )
            if order_item.quantity and order_item.quantity >= 1:
                has_valid_quantity = True
                total_price += order_item.price * order_item.quantity

        if not has_valid_quantity:
            raise HTTPException(
                status_code=400,
                detail="Order must include at least one valid menu item with quantity of 1 or more."
            )

        # Validate user owns card and fetch card details
        card = get_card_for_user(order_request.card_id, order_request.user_id)

        orders = load_all()

        order_id = str(uuid4())     #Generates a unique order ID using uuid4.
        timestamp = datetime.now(timezone.utc)     #records time for when order is created/updated/delivered
        
        new_order = CreateOrderResponse(
            order_id = order_id,
            user_id = order_request.user_id,
            restaurant_id = order_request.restaurant_id,
            items = order_request.items,
            status = DeliveryStatus.created,
            total_price = total_price,
            delivery_method= DeliveryType(order_request.delivery_method),
            delivery_address=order_request.delivery_address,
            pickup_location=order_request.pickup_location,
            created_at = timestamp,
            updated_at = timestamp,
            delivered_at = None
        )
        
        orders.append(new_order.model_dump(mode='json'))
        save_all(orders)
        
        # Generate payment transaction
        transaction = PaymentTransaction(
            payment_id = str(uuid4()),
            order_id = new_order.order_id,
            user_id = new_order.user_id, 
            status = PaymentStatusType.pending,
            card = card,
            created_at = timestamp,
            updated_at = timestamp,
            price_total = total_price
        )

        # Create payment transaction
        payment_status = create_transaction(transaction)
        
        # Generate a notification for the order creation event.
        self.notification.create_order_created_notification(user_id = new_order.user_id, order_id = new_order.order_id, restaurant_name = restaurant_name)

        return new_order
    
    # Tariq
    def get_order_by_id(self, order_id: str, current_user: User) -> Order:
        # Retrieve the order from the repository
        orders = load_all()

        # Iterate through orders list
        for o in orders:
            # Return the found order
            if str(o.get("order_id")) == order_id:
                #The authenticated user must match the requested user id. SR3 security check.
                if (current_user.id != str(o.get("user_id")) and current_user.role != "admin"):
                    raise HTTPException(status_code=403, detail=f"Not authorized to perform this action.")
                return Order(**o) 
                 
        raise HTTPException(status_code=404, detail="Order not found.") # Quick error handling for not found

    # Omarion/Siam [Notification]
    def update_order_status(self, update_order_id: str, status_request: OrderStatusUpdateRequest) -> Order:
        orders = load_all()
        # Search order list for order associated with update_order_id
        #this updated status of existing order and generates a notif when status changes. Essential for SR2.
        for idx, o in enumerate(orders):
            if str(o.get("order_id")) == update_order_id:        
                old_status = DeliveryStatus(o.get("status"))
                new_status = status_request.status
                # If status is the same
                if old_status == new_status:
                    raise HTTPException(status_code = 400, detail = "Order status remains unchanged.")  
                
                # Import get transaction by id function
                from app.services.payments_service import get_transaction_by_id

                # Check that order payment transaction is not declined
                if new_status != DeliveryStatus.cancelled:
                    transaction = get_transaction_by_id(update_order_id, str(o.get("user_id")))
                    if transaction.status == PaymentStatusType.declined:
                        raise HTTPException(status_code=400, detail="Cannot update order status with a declined payment.")

                # Transistion rules for order status
                if DeliveryType(o.get("delivery_method")) == DeliveryType.pickup:
                    allowed_next_statuses = PICKUP_STATUS_TRANSITIONS.get(old_status.value, [])
                else:
                    allowed_next_statuses = DELIVERY_STATUS_TRANSITIONS.get(old_status.value, [])

                if new_status.value not in allowed_next_statuses:
                    raise HTTPException(status_code=400, detail=f"Invalid status transition from '{old_status.value}' to '{new_status.value}'.")

                # Set timestamp for status update
                timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                
                o["status"] = new_status.value     #Update the order status 
                o["updated_at"] = timestamp
                
                if new_status == DeliveryStatus.delivered:
                    o["delivered_at"] = timestamp
                    
                orders[idx] = o     #Save the updated order 
                save_all(orders)
                
                restaurant_name = str(o.get("restaurant_name") or o.get("restaurant_id") or "Unknown Restaurant")
                
                #Now generate a notification for the order status change event.
                self.notification.create_order_status_changed_notification(
                    user_id = o["user_id"],
                    order_id = o["order_id"],
                    restaurant_name = restaurant_name,
                    old_status = old_status,
                    new_status = new_status
                )
                
                return Order(**o)
        #404 - not found if order ID does not exist 
        raise HTTPException(status_code = 404, detail = "Order not found.")    

    # Omarion
    # Update Order Delivery Status
    def assign_delivery_info(self, update_order_id: str, delivery_request: DeliveryInfoUpdateRequest) -> Order:
        orders = load_all()
        # Search order list for order associated with update_order_id
        for idx, o in enumerate(orders):
            if str(o.get("order_id")) == update_order_id:
                # Check if order cancelled or complete
                if DeliveryStatus(o.get("status")) in (DeliveryStatus.delivered, DeliveryStatus.picked_up, DeliveryStatus.complete, DeliveryStatus.cancelled):
                    raise HTTPException(status_code=400, detail="Cannot update an order that is completed or cancelled.")
                # Set new values
                if delivery_request.delivery_method is not None:
                    o["delivery_method"] = delivery_request.delivery_method
                if delivery_request.delivery_address is not None:
                    o["delivery_address"] = delivery_request.delivery_address
                if delivery_request.pickup_location is not None:
                    o["pickup_location"] = delivery_request.pickup_location
                o["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") # Convert to a string to prevent json save issues

                # Set order entry with updated values
                orders[idx] = o

                # Save changes to order
                save_all(orders)
                return Order(**o)
        raise HTTPException(status_code=404, detail="Order not found.")

    # Omarion
    # Update Order Information
    def update_order_info(self, update_order_id: str, items: List[OrderItem]):
        orders_store = load_all()
        # Search order list for order associated with update_order_id
        for idx, o in enumerate(orders_store):
            # Check if update_restaurant_id matches
            if str(o.get("order_id")) == str(update_order_id):
                # Import get transaction by id function
                from app.services.payments_service import get_transaction_by_id

                # Check that order payment transaction is not declined
                transaction = get_transaction_by_id(update_order_id, str(o.get("user_id")))
                if transaction.status == PaymentStatusType.declined:
                    raise HTTPException(status_code=400, detail="Cannot update order status with a declined payment.")
            
                # Check if order cancelled or complete
                if DeliveryStatus(o.get("status")) in (DeliveryStatus.delivered, DeliveryStatus.picked_up, DeliveryStatus.complete, DeliveryStatus.cancelled):
                    raise HTTPException(status_code=400, detail="Cannot update an order that is completed or cancelled.")
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

    # Siam
    def get_order_history_by_user_id(self, user_id: str) -> List[Order]:
        orders_store = load_all()
        user_orders: List[Order] = []
        
        # Search order list for order associated with update_order_id
        for idx, o in enumerate(orders_store):
            # Check if update_restaurant_id matches
            if str(o.get("user_id")) == str(user_id):
                user_orders.append(Order(**o))
        
        # Return list of orders
        return user_orders

    def reorder_past_order(self, original_order_id: str, reorder_request: ReorderRequest, current_user: User) -> CreateOrderResponse:
        # Retrieve the original order from the repository
        orders = load_all()
        original_order = None
        for o in orders:
            if str(o.get("order_id")) == str(original_order_id):
                original_order = o
                break
        
        if original_order is None:
            raise HTTPException(status_code=404, detail="Original order not found.")
        
        # Ensure the authenticated user is the owner of the original.
        #Now admins can reorder any order, but regular users can only reorder their own orders.
        #This is consistent with our security model for order retrieval and ensures users cannot reorder other users' orders.
        if current_user.id != str(original_order.get("user_id")) and current_user.role != "admin":                                                                                       
            raise HTTPException(status_code=403, detail="Not authorized to reorder this order.")
        
        # Override original order delivery method in reorder request if provided, otherwise use original delivery method
        delivery_method = (
            reorder_request.delivery_method
            if reorder_request.delivery_method is not None
            else original_order.get("delivery_method")
        )
        delivery_method = DeliveryType(delivery_method)
        
        # Handle only the fields relevant to delivery method override for simplicity.
        if delivery_method == DeliveryType.delivery:
            delivery_address = (
                reorder_request.delivery_address
                if reorder_request.delivery_address is not None
                else original_order.get("delivery_address")
            )
            pickup_location = None  # Clear pickup location if switching to delivery
            
            # Validate delivery or pickup requirements
            if not delivery_address:
                raise HTTPException(status_code=400, detail="delivery_address is required when delivery_method is 'delivery'.")
            
        else:
            pickup_location = (
                reorder_request.pickup_location
                if reorder_request.pickup_location is not None
                else original_order.get("pickup_location")
            )
            delivery_address = None  # Clear delivery address if switching to pickup
            
            # Validate delivery or pickup requirements
            if not pickup_location:
                raise HTTPException(status_code=400, detail="pickup_location is required when delivery_method is 'pickup'.")

        # Build a new order request using the past order's details. 
        reordered_order_request = CreateOrderRequest(
            # The user_id for the new order will be the same as the original order, which is the current authenticated user. 
            #We enforce this in the security check above to ensure users can only reorder their own orders (unless admin).
            user_id = str(original_order["user_id"]),       
            card_id = reorder_request.card_id,
            restaurant_id = original_order["restaurant_id"],
            items = [OrderItem(**item) for item in original_order["items"]],
            delivery_method = delivery_method,
            delivery_address = delivery_address,
            pickup_location = pickup_location
        )
        # Create and return a new order
        return self.create_order(reordered_order_request)