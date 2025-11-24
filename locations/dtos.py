from decimal import Decimal

from pydantic import BaseModel


class LocationDTO(BaseModel):
    name: str
    country_code: str
    latitude: Decimal
    longitude: Decimal
    is_adding: bool
