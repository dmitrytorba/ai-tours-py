import json
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from typing import Annotated, List
import requests

load_dotenv()


@tool
def reverse_geocode(
    latlng: Annotated[str, "comma seperated latitude and logitude"]
) -> any:
    """Get the address and other geographical information of a given latitude and longitude"""
    r = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?latlng={}&extra_computations=ADDRESS_DESCRIPTORS&key={}".format(
            latlng, os.environ["GOOGLE_API_KEY"]
        )
    )
    locations = r.json()
    return locations


@tool
def nearby_places(
    latitude: Annotated[str, "latitude"], longitude: Annotated[str, "logitude"], radius: Annotated[int, "radius in meters"]
) -> any:
    """Get places around a given latitude, longitude and radius"""
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Goog-Api-Key": os.environ["GOOGLE_API_KEY"],
        "X-Goog-FieldMask": "places.attributions,places.businessStatus,places.containingPlaces,places.displayName,places.formattedAddress,places.id,places.location,places.primaryType,places.primaryTypeDisplayName,places.pureServiceAreaBusiness,places.subDestinations,places.types",
    }
    payload = {
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius  
            }
        },
    }
    r = requests.post(
        "https://places.googleapis.com/v1/places:searchNearby",
        data=json.dumps(payload),
        headers=headers,
    )
    locations = r.json()
    return locations


if __name__ == "__main__":
    print(reverse_geocode.invoke("40.748817,-73.985428"))
