from backend.app.routers.orders import router as orders_router
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "OK"}

app.include_router(orders_router)     #Include the orders router to make the order creation endpoint available.