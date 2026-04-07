import pytest
from datetime import datetime
from fastapi import HTTPException
from app.services.restaurants_service import RestaurantsService
from app.services.orders_service import OrdersService
from app.schemas.order import CreateOrderRequest, OrderItem

class FakeRestaurantsRepository:
    def load_all(self):
        return [
            {
                "restaurant_id": "1",
                "restaurant_name": "Pizza Place",
                "isOpen": True,
                "opening_time": "09:00",
                "closing_time": "21:00",
                "tags": [],
                "menuItems": []
            }
        ]
    
service = RestaurantsService(FakeRestaurantsRepository())
service._current_time_override = datetime.strptime("10:00", "%H:%M").time()

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


def test_is_restaurant_open_true():
    service = OrdersService()
    service._current_time_override = datetime.strptime("12:00", "%H:%M").time()

    restaurant = {
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00"
    }

    assert service._is_restaurant_open(restaurant) is True

def test_is_restaurant_open_false_outside_hours():
    service = OrdersService()
    service._current_time_override = datetime.strptime("22:00", "%H:%M").time()

    restaurant = {
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00"
    }

    assert service._is_restaurant_open(restaurant) is False

def test_is_restaurant_open_false_when_manually_closed():
    service = OrdersService()
    service._current_time_override = datetime.strptime("12:00", "%H:%M").time()

    restaurant = {
        "isOpen": False,
        "opening_time": "09:00",
        "closing_time": "21:00"
    }

    assert service._is_restaurant_open(restaurant) is False


def test_restaurant_open_during_hours():
    service = RestaurantsService(FakeRestaurantsRepository())
    service._current_time_override = datetime.strptime("10:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "1",
        "restaurant_name": "Pizza Place",
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00",
        "tags": [],
        "menuItems": []
    }

    assert service._is_restaurant_open_now(restaurant) is True

def test_restaurant_closed_outside_hours():
    service = RestaurantsService(FakeRestaurantsRepository())
    service._current_time_override = datetime.strptime("22:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "1",
        "restaurant_name": "Pizza Place",
        "isOpen": True,
        "opening_time": "09:00",
        "closing_time": "21:00",
        "tags": [],
        "menuItems": []
    }

    assert service._is_restaurant_open_now(restaurant) is False

def test_restaurant_open_overnight():
    service = RestaurantsService(FakeRestaurantsRepository())
    service._current_time_override = datetime.strptime("01:00", "%H:%M").time()

    restaurant = {
        "restaurant_id": "1",
        "restaurant_name": "Late Night Food",
        "isOpen": True,
        "opening_time": "18:00",
        "closing_time": "02:00",
        "tags": [],
        "menuItems": []
    }

    assert service._is_restaurant_open_now(restaurant) is True