from enum import StrEnum

# Delivery Types - Delivery or Pickup
class DeliveryType (StrEnum):
    delivery = "delivery"
    pickup = "pickup"

# Delivery Statuses - Created, Preparing, Ready, Complete
class DeliveryStatus (StrEnum):
    created = "created"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    picked_up = "pickedup"
    complete = "completed"