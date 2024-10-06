from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from typing import Annotated, List
import requests

load_dotenv()


@tool
def reverse_geocode(latlng: Annotated[str, "comma seperated latitude and logitude"]) -> any:
    """Get the address and other geographical information of a given latitude and longitude"""
    r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng={}&key={}'.format(latlng, os.environ["GOOGLE_API_KEY"]))
    locations = r.json()
    return locations



if __name__ == "__main__":
    print(reverse_geocode.invoke("40.748817,-73.985428"))