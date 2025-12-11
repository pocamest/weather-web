from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, TypedDict

from django.http import HttpResponse

from locations.models import Location

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse as DjangoTestResponse

    from users.models import User
else:
    DjangoTestResponse = HttpResponse


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
