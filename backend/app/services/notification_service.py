from typing import List
from datetime import datetime, timezone
from app.schemas.notification import Notification  

class NotificationService:
    #This is the in-memory notification service. Since there is no database, we will store notifications in a list. However, notifications disappear when application restarts.
    notifications: List[Notification] = []
    def __init__(self) -> None:
        pass
    
    def create_order_created_notification(self, user_id: str, order_id: str) -> Notification:
        """Generates a notification for an order created new. key method for SR1.
        """
        notification = Notification(
            user_id = user_id,
            order_id = order_id,
            type = "Order_Created",
            title = "Order Created",
            message = f"Your order {order_id} has been created successfully.",
            timestamp=datetime.now(timezone.utc)
        )
        self.notifications.append(notification)     #Store the notification in memory to retrieve it later if needed.
        return notification
    
   
    def create_order_status_changed_notification(self, user_id: str, order_id: str, old_status: str, new_status: str) -> Notification:
        """A notification is generated when an order status is changed. A requirement for SR2"""
        notification = Notification(
            user_id = user_id,
            order_id = order_id,
            type = "Order_Status_Changed",
            title = "Order Status Updated",
            message = f"Your order {order_id} status has been changed from {old_status} to {new_status}.",
            timestamp=datetime.now(timezone.utc)
        )
        self.notifications.append(notification)     #Store the notification in memory to retrieve it later if needed.
        return notification
    
    def get_notifications_for_user(self, user_id: str) -> List[Notification]:
        return [n for n in self.notifications if n.user_id == user_id]
        
    def clear_notifications(self) -> None:
        self.notifications.clear()     #This clears all notifs from memory. 

    #For SR3, we will be storing unauthorized access attempts
    # unauthorized_access_log: List[dict] = []
    # logger = logging.getLogger(__name__)        #creates a python logger for server logs

    # def validate_access_to_order_history(requested_user_id: str, authenticated_user_id: Optional[str], path: str) -> None:
        
    #     #Unauthenticated user requests rejected
    #     if authenticated_user_id is None:
    #         attempt = {"requested_user_id": requested_user_id, "authenticated_user_id": None, "path": path, "timestamp": datetime.now(timezone.utc)}
    #         unauthorized_access_log.append(attempt)
    #         logger.warning("Unauthorized attempt: order history access rejected: %s", attempt)
    #         raise HTTPException(status_code = 401, detail = "Authentication required.")
        
    #     #Accessing other user data requests rejected
    #     if authenticated_user_id != requested_user_id:
    #         attempt = {"requested_user_id": requested_user_id, "authenticated_user_id": authenticated_user_id, "path": path, "timestamp": datetime.now(timezone.utc)}
    #         unauthorized_access_log.append(attempt)
    #         logger.warning("Unauthorized attempt: forbidden order history access: %s", attempt)
    #         raise HTTPException(status_code = 403, detail = "Not authorized to access this order history.")
        