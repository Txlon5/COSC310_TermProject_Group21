from fastapi import APIRouter
from typing import List
from app.routers.orders import notification
from app.schemas.notification import Notification

router = APIRouter()

@router.get("/notifications/{user_id}", response_model = List[Notification])
def get_notifications_for_user(user_id: str) -> List[Notification]:
    #This endpoint retrieves all notifications for a specific user. Requirement for SR3.
    return notification.get_notifications_for_user(user_id)

"""Thought of approach: from app.routers.orders import notification resuses the same instance of NotificationService created in orders.py. 
This allows us to access the notifications stored in memory when orders are created or updated. The get_notifications_for_user method retrieves all notifications for a specific user, which is essential for SR3. 
Since we are using in-memory storage, all notifications will be lost when the application restarts, but this is acceptable for the scope of this project. Subject to review."""