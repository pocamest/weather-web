from collections.abc import Callable
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from django.contrib.auth.models import AnonymousUser

from locations.dtos import LocationDTO
from locations.models import Location
from locations.schemas import LocationSearchSchema
from locations.services import LocationService

from .test_types import LocationData

if TYPE_CHECKING:
    from users.models import User


@pytest.mark.django_db
def test_search_correctly_flags_added_locations(
    test_user: 'User',
    moscow_ru_data: LocationData,
    moscow_us_data: LocationData,
    create_location: Callable[..., Location],
    mock_weather_client: MagicMock,
    location_service: LocationService,
) -> None:
    query = moscow_ru_data['name']
    create_location(location_data=moscow_ru_data, user=test_user)
    create_location(location_data=moscow_us_data)

    mock_weather_client.search_locations.return_value = [
        LocationSearchSchema(**moscow_ru_data),
        LocationSearchSchema(**moscow_us_data),
    ]

    search_results = location_service.search(query=query, user=test_user)

    mock_weather_client.search_locations.assert_called_once_with(query)

    expected_moscow_ru = LocationDTO(**moscow_ru_data, is_added=True)
    expected_moscow_us = LocationDTO(**moscow_us_data, is_added=False)

    assert search_results == [expected_moscow_ru, expected_moscow_us]


@pytest.mark.django_db
def test_search_location_for_anonymous_user(
    moscow_ru_data: LocationData,
    mock_weather_client: MagicMock,
    location_service: LocationService,
) -> None:
    mock_weather_client.search_locations.return_value = [
        LocationSearchSchema(**moscow_ru_data)
    ]

    query = moscow_ru_data['name']
    anonymous_user = AnonymousUser()

    search_results = location_service.search(query=query, user=anonymous_user)

    mock_weather_client.search_locations.assert_called_once_with(query)

    expected_dto = LocationDTO(**moscow_ru_data, is_added=False)

    assert search_results == [expected_dto]
