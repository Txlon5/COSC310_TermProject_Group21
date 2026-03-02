from fastapi import FastAPI

from app.data.restaurants_data import RESTAURANTS # Grabbing the RESTAURTANTS class

# RESTAURANT STUFF - I am unsure if we will put all imports and such in main?
from typing import List
from app.schemas.restaurants import RestaurantOut
from app.repositories.restaurants_repository import RestaurantsRepository
from app.services.restaurants_service import RestaurantsService
# END Restaurant imports

app = FastAPI()
@app.get("/")
def hello():
    return {"msg": "Hello World"}
@app.get("/items/{name}")
def get_item(name: str):
    return {"item": name, "status": "ok"}

@app.get("/debug")
def debug_data():
    return RESTAURANTS # Trying to see if I can get a response from RESTAURANTS

# Create repository instance
# This object is responsible for retrieving restaurant data
restaurants_repository = RestaurantsRepository()

# Inject repository into the service
# The service will call the repository internally
restaurants_service = RestaurantsService(restaurants_repository)

# Using the endpoint, response_model ensures returned data matches RestaurantOut schema
@app.get("/restaurants", response_model=List[RestaurantOut])
def get_restaurants():

    restaurants = restaurants_service.get_restaurants() # Call business logic layer

    return restaurants # Return result to client