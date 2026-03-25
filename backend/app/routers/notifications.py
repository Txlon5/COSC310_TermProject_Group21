from fastapi import APIRouter
from typing import List
from app.services.notification_service import NotificationService
from app.schemas.notification import Notification

router = APIRouter(prefix = "/notifications", tags = ["Notifications"])

@router.get("/{user_id}", response_model = List[Notification])
def get_notifications_for_user(user_id: str) -> List[Notification]:
    #This endpoint retrieves all notifications for a specific user. Requirement for SR3.
    notification = NotificationService()
    return notification.get_notifications_for_user(user_id)