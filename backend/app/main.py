from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from app.routers.menus import router as menus_router
from app.routers.orders import router as orders_router
from app.routers.users import router as users_router
from app.routers.restaurants_router import router as restaurants_router
from app.routers.auth import router as auth_router
from app.routers.notifications import router as notifications_router

app = FastAPI()
app.include_router(orders_router)   #Include the orders router to make the order creation endpoint available.
app.include_router(users_router)    #Include the users router to make user management endpoints available.
app.include_router(auth_router)     #Include the auth router to make authentication endpoints available.
app.include_router(notifications_router, tags = ["Notifications"])    #Include the notifications router to make the notifications retrieval endpoint available.
app.include_router(restaurants_router) # Include the restaurants router to make the restaurant listing and search endpoints available.
app.include_router(menus_router)

@app.get("/")
def root():
    return {"message": "Backend running"}
