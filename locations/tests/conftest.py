from unittest.mock import MagicMock

import pytest

from locations.services import LocationService


@pytest.fixture
def mock_weather_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def location_service(mock_weather_client: MagicMock) -> LocationService:
    return LocationService(weather_client=mock_weather_client)
