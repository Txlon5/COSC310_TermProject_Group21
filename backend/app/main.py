from fastapi import FastAPI
from app.routers.orders import router as orders_router
from app.routers.users import router as users_router
from app.routers.restaurants_router import router as restaurants_router


app = FastAPI()
app.include_router(orders_router)
app.include_router(users_router)
app.include_router(restaurants_router)
