from fastapi import FastAPI
from app.routers.menus import router as menus_router

app = FastAPI()

app.include_router(menus_router)

@app.get("/")
def root():
    return {"message": "API is running"}