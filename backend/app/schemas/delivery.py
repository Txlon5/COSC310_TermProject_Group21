from enum import Enum

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# Delivery Types - Delivery or Pickup
class DeliveryType (str, Enum):
    delivery = "delivery"
    pickup = "pickup"

# Delivery Statuses - Created, Preparing, Ready, Complete
class DeliveryStatus (str, Enum):
    created = "Created"
    preparing = "Preparing"
    ready = "Ready"
    delivered = "Delivered"
    picked_up = "Picked up"
    complete = "Completed"