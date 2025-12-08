from decimal import Decimal
from typing import TypedDict


class LocationData(TypedDict):
    name: str
    country_code: str
    latitude: Decimal
    longitude: Decimal
