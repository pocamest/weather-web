from decimal import Decimal

from pydantic import (
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
)


class LocationSearchSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

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
        return v[:255]


location_search_adapter = TypeAdapter(list[LocationSearchSchema])


class WeatherSchema(BaseModel):
    temperature: Decimal = Field(
        max_digits=5,
        decimal_places=2,
        ge=-100,
        le=100,
        validation_alias=AliasPath('main', 'temp'),
    )
