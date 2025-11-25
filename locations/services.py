from typing import TYPE_CHECKING

from .clients import OpenWeatherClient
from .dtos import LocationDTO
from .models import Location

if TYPE_CHECKING:
    from users.models import User


class LocationService:
    def __init__(self, weather_client: OpenWeatherClient) -> None:
        self.weather_client = weather_client

    def search_locations(self, query: str, user: 'User') -> list[LocationDTO]:
        search_results = self.weather_client.search_locations(query)
        search_geo_keys = [
            Location.generate_geo_key(latitude=item.latitude, longitude=item.longitude)
            for item in search_results
        ]
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
