from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    """This is the model for notification. 
        This gets stored only in memory for the lifetime of the app since there's no database.
    """
    user_id: str
    restaurant_name: str
    order_id: str
    type: str
    title: str
    message: str
    timestamp: datetime
    