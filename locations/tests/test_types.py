from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, TypedDict

from locations.models import Location

if TYPE_CHECKING:
    from users.models import User


class LocationData(TypedDict):
    name: str
    country_code: str
    latitude: Decimal
    longitude: Decimal


class CreateLocationCallable(Protocol):
    def __call__(
        self, location_data: LocationData, user: 'User | None' = None
    ) -> Location: ...
