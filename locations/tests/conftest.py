from decimal import Decimal
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from locations.models import Location
from locations.services import LocationService

from .test_types import CreateLocationCallable, LocationData

if TYPE_CHECKING:
    from users.models import User


@pytest.fixture
def mock_weather_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def location_service(mock_weather_client: MagicMock) -> LocationService:
    return LocationService(weather_client=mock_weather_client)


@pytest.fixture
def create_location(db: Any) -> CreateLocationCallable:
    def _create_location(
        location_data: LocationData, user: 'User | None' = None
    ) -> Location:
        location = Location.objects.create(**location_data)
        if user:
            user.locations.add(location)
        return location

    return _create_location


@pytest.fixture
def moscow_ru_data() -> LocationData:
    return {
        'name': 'Moscow',
        'country_code': 'RU',
        'latitude': Decimal('55.7504461'),
        'longitude': Decimal('37.6174943'),
    }


@pytest.fixture
def moscow_us_data() -> LocationData:
    return {
        'name': 'Moscow',
        'country_code': 'US',
        'latitude': Decimal('46.7323875'),
        'longitude': Decimal('-117.0001651'),
    }


@pytest.fixture
def london_gb_data() -> LocationData:
    return {
        'name': 'London',
        'country_code': 'GB',
        'latitude': Decimal('51.5073219'),
        'longitude': Decimal('-0.1276474')
    }
