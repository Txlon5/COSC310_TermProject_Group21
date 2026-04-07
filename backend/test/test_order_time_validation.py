import pytest
from datetime import datetime
from fastapi import HTTPException

from app.services.orders_service import OrdersService
from app.schemas.order import CreateOrderRequest, OrderItem


def test_is_restaurant_open_returns_true_when_time_is_within_hours():
    service = OrdersService()
    service._get_current_time = lambda: datetime.strptime("22:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "rest1",
        "restaurant_name": "Pizza Place",
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00",
        "tags": ["pizza"],
        "menuItems": []
    }

    assert service._is_restaurant_open(restaurant) is False


def test_is_restaurant_open_returns_false_when_time_is_outside_hours():
    service = OrdersService()
    service._get_current_time = lambda: datetime.strptime("22:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "rest1",
        "restaurant_name": "Pizza Place",
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00",
        "tags": ["pizza"],
        "menuItems": []
    }

    assert service._is_restaurant_open(restaurant) is False


def test_is_restaurant_open_returns_false_when_restaurant_is_manually_closed():
    service = OrdersService()
    service._get_current_time = lambda: datetime.strptime("12:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "rest1",
        "restaurant_name": "Pizza Place",
        "isOpen": False,
        "opening_time": "09:00",
        "closing_time": "21:00",
        "tags": ["pizza"],
        "menuItems": []
    }

    assert service._is_restaurant_open(restaurant) is False