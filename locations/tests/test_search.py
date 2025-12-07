from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import MagicMock

import pytest

from locations.dtos import LocationDTO
from locations.models import Location
from locations.schemas import LocationSearchSchema
from locations.services import LocationService

if TYPE_CHECKING:
    from users.models import User


class LocationData(TypedDict):
    name: str
    country_code: str
    latitude: Decimal
    longitude: Decimal


@pytest.fixture
def added_location_data() -> LocationData:
    return {
        'name': 'Moscow',
        'country_code': 'RU',
        'latitude': Decimal('55.7504461'),
        'longitude': Decimal('37.6174943'),
    }


@pytest.fixture
def new_location_data() -> LocationData:
    return {
        'name': 'Moscow',
        'country_code': 'US',
        'latitude': Decimal('46.7323875'),
        'longitude': Decimal('-117.0001651'),
    }


@pytest.fixture
def create_location(db: Any) -> Callable[..., Location]:
    def _create_location(
        location_data: LocationData, user: 'User | None' = None
    ) -> Location:
        location = Location.objects.create(**location_data)
        if user:
            user.locations.add(location)
        return location

    return _create_location


@pytest.mark.django_db
def test_search_correctly_flags_added_locations(
    test_user: 'User',
    added_location_data: LocationData,
    new_location_data: LocationData,
    create_location: Callable[..., Location],
    mock_weather_client: MagicMock,
    location_service: LocationService,
) -> None:
    query = added_location_data['name']
    create_location(location_data=added_location_data, user=test_user)
    create_location(location_data=new_location_data)

    mock_weather_client.search_locations.return_value = [
        LocationSearchSchema(**added_location_data),
        LocationSearchSchema(**new_location_data),
    ]

    search_results = location_service.search(query=query, user=test_user)

    mock_weather_client.search_locations.assert_called_once_with(query)

    expected_added_dto = LocationDTO(**added_location_data, is_added=True)
    expected_new_dto = LocationDTO(**new_location_data, is_added=False)

    assert search_results == [expected_added_dto, expected_new_dto]
