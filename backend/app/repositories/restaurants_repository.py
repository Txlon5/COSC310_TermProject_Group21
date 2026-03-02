# To my udnerstanding, this file helps us swap the data source for restaurants later
# Which is good consiodering I want to go from a list, to CSV, then eventually our database.

from app.data.restaurants_data import RESTAURANTS # To not rewrite it fully


class RestaurantsRepository:# This is the class that fetches the data.
    def get_all(self):
        return RESTAURANTS