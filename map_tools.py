from langchain_core.tools import tool
from dotenv import load_dotenv
from typing import Annotated, List

load_dotenv()


@tool
def move_map(lat: Annotated[str, "latitude"], lng: Annotated[str, "logitude"], label: Annotated[str, "map pin label"]) -> any:
    """Move the users map center to a given latitude and longitude, placing a pin with a label"""
    return "Map moved to {},{}".format(lat, lng)


