import logging
from collections.abc import Iterable
from decimal import Decimal
from typing import TYPE_CHECKING

from .clients import OpenWeatherClient
from .dtos import LocationDTO, LocationWithWeatherDTO
from .exceptions import APIError
from .models import Location

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser

    from users.models import User

logger = logging.getLogger(__name__)


class LocationService:
    def __init__(self, weather_client: OpenWeatherClient) -> None:
        self.weather_client = weather_client

    def search(self, query: str, user: 'User | AnonymousUser') -> list[LocationDTO]:
        search_results = self.weather_client.search_locations(query)
        search_geo_keys = [
            Location.generate_geo_key(latitude=item.latitude, longitude=item.longitude)
            for item in search_results
        ]

        user_added_geo_keys = set()
        if user.is_authenticated:
            user_added_geo_keys = set(
                user.locations.filter(geo_key__in=search_geo_keys).values_list(
                    'geo_key', flat=True
                )
            )

        results = []
        for geo_key, item in zip(search_geo_keys, search_results):
            is_added = geo_key in user_added_geo_keys
            results.append(
                LocationDTO(
                    name=item.name,
                    country_code=item.country_code,
                    latitude=item.latitude,
                    longitude=item.longitude,
                    is_added=is_added,
                )
            )
        return results

    def add(
        self,
        user: 'User',
        name: str,
        country_code: str,
        latitude: Decimal,
        longitude: Decimal,
    ) -> Location:
        geo_key = Location.generate_geo_key(latitude=latitude, longitude=longitude)
        location, _ = Location.objects.get_or_create(
            geo_key=geo_key,
            defaults={
                'name': name,
                'country_code': country_code,
                'latitude': latitude,
                'longitude': longitude,
            },
        )
        user.locations.add(location)

        return location

    def get_locations_with_weather(
        self, user_locations: Iterable[Location]
    ) -> list[LocationWithWeatherDTO]:
        results = []
        for location_db in user_locations:
            try:
                location_schema = self.weather_client.get_weather(
                    lat=location_db.latitude, lon=location_db.longitude
                )
                location_dto = LocationWithWeatherDTO(
                    name=location_schema.location_name,
                    country_code=location_schema.country_code,
                    temperature=location_schema.temperature,
                )
            except APIError:
                logger.exception('API call failed')
                location_dto = LocationWithWeatherDTO(
                    name=location_db.name,
                    country_code=location_db.country_code,
                    temperature=None,
                )
            results.append(location_dto)
        return results
