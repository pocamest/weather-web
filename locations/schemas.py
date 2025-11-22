from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class LocationSearchSchema(BaseModel):
    name: str
    country_code: str = Field(max_length=2, validation_alias='country')
    latitude: Decimal = Field(
        max_digits=9, decimal_places=7, ge=-90, le=90, validation_alias='lat'
    )
    longitude: Decimal = Field(
        max_digits=10, decimal_places=7, ge=-180, le=180, validation_alias='lon'
    )

    @field_validator('name')
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip()[:255]
