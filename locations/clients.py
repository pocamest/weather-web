from decimal import Decimal
from typing import Any

import requests
from django.conf import settings

from .exceptions import APIError


class OpenWeatherClient:
    GEOCODING_URL = 'http://api.openweathermap.org/geo/1.0/direct'
    CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
    DEFAULT_TIMEOUT = (2, 10)

    def __init__(
        self,
        api_key: str = settings.OPEN_WEATHER_API_KEY,
        timeout: tuple[int, int] = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.timeout = timeout

    def _execute_get_request(self, url: str, params: dict[str, Any]) -> Any:
        try:
            response = requests.get(url=url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise APIError(f'API request failed: {e}') from e
        return response.json()

    def find_locations_by_name(
        self, name: str, limit: int = settings.OPEN_WEATHER_DEFAULT_SEARCH_LIMIT
    ) -> list[dict[str, Any]]:
        params: dict[str, str | int] = {
            'q': name,
            'limit': limit,
            'appid': self.api_key,
        }
        response: list[dict[str, Any]] = self._execute_get_request(
            url=self.GEOCODING_URL, params=params
        )
        return response

    def find_weather_by_coordinates(
        self,
        lat: Decimal,
        lon: Decimal,
        units: str = settings.OPEN_WEATHER_DEFAULT_UNITS,
    ) -> dict[str, Any]:
        params: dict[str, str] = {
            'lat': str(lat),
            'lon': str(lon),
            'units': units,
            'appid': self.api_key,
        }
        response: dict[str, Any] = self._execute_get_request(
            url=self.CURRENT_WEATHER_URL, params=params
        )
        return response
