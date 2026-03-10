from typing import List
from datetime import datetime
from app.schemas.notification import Notification  

class NotificationService:
    #This is the in-memory notification service. Since there is no database, we will store notifications in a list. However, notifications disappear when application restarts.
    def __init__(self) -> None:
        self.notifications: List[Notification] = []
    
    def create_order_created_notification(self, user_id: str, order_id: str) -> Notification:
        """Generates a notification for an order created new. key method for SR1.
        """
        notification = Notification(
            user_id = user_id,
            order_id = order_id,
            type = "Order Created",
            title = "Your order has been created!",
            message = f"Your order has been successfully created. Order ID: {order_id}",
            timestamp=datetime.now()
        )
        self.notifications.append(notification)     #Store the notification in memory to retrieve it later if needed.
        return notification
    
    def get_notifications_for_user(self, user_id: str) -> List[Notification]:
        return [n for n in self.notifications if n.user_id == user_id]      #This allows  returns all notifs for a specific user. will need this in SR3
    
    def clear_notifications(self) -> None:
        self.notifications.clear()     #This clears all notifs from memory. 