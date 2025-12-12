from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, TypedDict

from locations.models import Location
from test_utils.types import DjangoTestResponse

if TYPE_CHECKING:
    from users.models import User


class LocationData(TypedDict):
    name: str
    country_code: str
    latitude: Decimal
    longitude: Decimal


class LocationInvalidData(TypedDict):
    invalid_data: str


class CreateLocationCallable(Protocol):
    def __call__(
        self, location_data: LocationData, user: 'User | None' = None
    ) -> Location: ...


class AddLocationCallable(Protocol):
    def __call__(
        self,
        location_data: LocationData | LocationInvalidData,
        user: 'User | None' = None,
    ) -> DjangoTestResponse: ...
