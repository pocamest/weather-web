from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from locations.dtos import LocationWithWeatherDTO
from locations.exceptions import APIError
from locations.schemas import WeatherSchema
from locations.services import LocationService

from .test_types import CreateLocationCallable, LocationData


@pytest.mark.django_db
def get_locations_with_weather_with_success_and_api_error(
    moscow_ru_data: LocationData,
    moscow_us_data: LocationData,
    london_gb_data: LocationData,
    create_location: CreateLocationCallable,
    mock_weather_client: MagicMock,
    location_service: LocationService,
) -> None:
    first_location = create_location(moscow_ru_data)
    fail_location = create_location(moscow_us_data)
    last_location = create_location(london_gb_data)


    first_location_temp = Decimal('1')
    last_location_temp = Decimal('2')

    mock_weather_client.get_weather.side_effect = [
        WeatherSchema(temperature=first_location_temp),
        APIError('API request failed'),
        WeatherSchema(temperature=last_location_temp),
    ]

    locations_with_weather = location_service.get_locations_with_weather(
        [first_location, fail_location, last_location]
    )

    assert mock_weather_client.get_weather.call_count == 3

    expected_first_dto = LocationWithWeatherDTO(
        name=first_location.name,
        country_code=first_location.country_code,
        temperature=first_location_temp,
        location_id=first_location.id,
    )
    expected_fail_dto = LocationWithWeatherDTO(
        name=fail_location.name,
        country_code=fail_location.country_code,
        temperature=None,
        location_id=fail_location.id,
    )
    expected_last_dto = LocationWithWeatherDTO(
        name=last_location.name,
        country_code=last_location.country_code,
        temperature=last_location_temp,
        location_id=last_location.id,
    )

    assert len(locations_with_weather) == 3

    assert locations_with_weather[0] == expected_first_dto
    assert locations_with_weather[1] == expected_fail_dto
    assert locations_with_weather[2] == expected_last_dto
