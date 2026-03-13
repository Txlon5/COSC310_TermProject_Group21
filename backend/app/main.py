from fastapi import FastAPI
from app.routes.order import router as order_router
from app.routers.users import router as users_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "OK"}

app.include_router(order_router)     #Include the orders router to make the order creation endpoint available.
app.include_router(users_router)  