from decimal import Decimal
from typing import Any

import requests
from django.conf import settings
from pydantic import ValidationError

from .exceptions import APIError
from .schemas import LocationSearchSchema, WeatherSchema, location_search_adapter


class OpenWeatherClient:
    GEOCODING_URL = 'http://api.openweathermap.org/geo/1.0/direct'
    CURRENT_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'
    DEFAULT_TIMEOUT = (2, 10)

    def __init__(
        self,
        api_key: str | None = None,
        timeout: tuple[int, int] = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or settings.OPEN_WEATHER_API_KEY
        self.timeout = timeout

    def _execute_get_request(self, url: str, params: dict[str, Any]) -> Any:
        try:
            response = requests.get(url=url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise APIError(f'API request failed: {e}') from e
        return response.json()

    def search_locations(
        self, name: str, limit: int | None = None
    ) -> list[LocationSearchSchema]:
        limit = limit or settings.OPEN_WEATHER_DEFAULT_SEARCH_LIMIT

        params: dict[str, str | int] = {
            'q': name,
            'limit': limit,
            'appid': self.api_key,
        }
        response: list[dict[str, Any]] = self._execute_get_request(
            url=self.GEOCODING_URL, params=params
        )

        try:
            locations_search = location_search_adapter.validate_python(response)
        except ValidationError as e:
            raise APIError(f'API request failed: {e}') from e

        return locations_search

    def get_weather(
        self,
        lat: Decimal,
        lon: Decimal,
        units: str | None = None,
    ) -> WeatherSchema:
        units = units or settings.OPEN_WEATHER_DEFAULT_UNITS

        params: dict[str, str] = {
            'lat': str(lat),
            'lon': str(lon),
            'units': units,
            'appid': self.api_key,
        }
        response: dict[str, Any] = self._execute_get_request(
            url=self.CURRENT_WEATHER_URL, params=params
        )
        try:
            weather = WeatherSchema.model_validate(response)
        except ValidationError as e:
            raise APIError(f'API request failed: {e}') from e
        return weather
