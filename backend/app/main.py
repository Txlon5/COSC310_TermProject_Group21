from app.routers.orders import router as orders_router
from fastapi import FastAPI
from app.routers.users import router as users_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "OK"}

app.include_router(orders_router)     #Include the orders router to make the order creation endpoint available.
app.include_router(users_router)    #Include the users router to make user management endpoints available.
