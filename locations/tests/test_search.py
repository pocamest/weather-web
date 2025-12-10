from collections.abc import Callable
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.urls import reverse

from locations.dtos import LocationDTO
from locations.exceptions import APIError
from locations.models import Location
from locations.schemas import LocationSearchSchema
from locations.services import LocationService

from .test_types import LocationData

if TYPE_CHECKING:
    from users.models import User


@pytest.mark.django_db
def test_search_returns_locations_with_added_flags(
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

    assert len(search_results) == 2

    assert search_results[0] == expected_moscow_ru
    assert search_results[1] == expected_moscow_us


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


@patch('locations.views.OpenWeatherClient')
@pytest.mark.django_db
def test_search_page_handles_api_error(
    mock_client_class: MagicMock,
    client: Client,
    test_user: 'User',
) -> None:
    mock_instance = mock_client_class.return_value
    mock_instance.search_locations.side_effect = APIError('API request failed')

    url_search = reverse('locations:search')
    query = 'Moscow'
    query_params = {'query': query}

    client.force_login(test_user)

    response = client.get(path=url_search, query_params=query_params)

    mock_instance.search_locations.assert_called_once_with(query)

    assert response.status_code == 200

    messages = (str(m) for m in response.context['messages'])

    assert 'Connection error, please try again later' in messages
