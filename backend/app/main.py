from fastapi import FastAPI
from app.routers.restaurants import router as restaurants_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend running"}

app.include_router(restaurants_router)