from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client
from django.urls import reverse

from locations.models import Location
from test_utils.types import DjangoTestResponse

from .test_types import (
    AddLocationCallable,
    CreateLocationCallable,
    LocationData,
    LocationInvalidData,
)

if TYPE_CHECKING:
    from users.models import User


@pytest.fixture
def add_location(db: Any, client: Client) -> AddLocationCallable:
    def _add_location(
        location_data: LocationData | LocationInvalidData, user: 'User | None' = None
    ) -> DjangoTestResponse:
        url_add = reverse('locations:add')
        if user is not None:
            client.force_login(user)
        return client.post(path=url_add, data=location_data)

    return _add_location


@pytest.mark.django_db
def test_successful_add_new_location_in_db(
    test_user: 'User',
    moscow_ru_data: LocationData,
    add_location: AddLocationCallable,
) -> None:
    response = add_location(location_data=moscow_ru_data, user=test_user)

    assert response.status_code == 302

    assert Location.objects.count() == 1
    created_location = Location.objects.first()
    assert created_location is not None

    assert created_location.name == moscow_ru_data['name']
    assert created_location.country_code == moscow_ru_data['country_code']
    assert created_location.latitude == moscow_ru_data['latitude']
    assert created_location.longitude == moscow_ru_data['longitude']

    geo_key = Location.generate_geo_key(
        latitude=moscow_ru_data['latitude'], longitude=moscow_ru_data['longitude']
    )
    assert created_location.geo_key == geo_key

    assert created_location.users.count() == 1
    assert created_location.users.first() == test_user


@pytest.mark.django_db
def test_successful_created_link_between_location_and_user(
    test_user: 'User',
    moscow_ru_data: LocationData,
    create_location: CreateLocationCallable,
    add_location: AddLocationCallable,
) -> None:
    existing_location = create_location(location_data=moscow_ru_data)

    response = add_location(location_data=moscow_ru_data, user=test_user)

    assert response.status_code == 302

    assert Location.objects.count() == 1

    assert test_user.locations.count() == 1
    link_location = test_user.locations.first()
    assert link_location is not None

    assert link_location == existing_location


@pytest.mark.django_db
def test_add_link_location_no_change_db(
    test_user: 'User',
    moscow_ru_data: LocationData,
    create_location: CreateLocationCallable,
    add_location: AddLocationCallable,
) -> None:
    create_location(location_data=moscow_ru_data, user=test_user)

    response = add_location(location_data=moscow_ru_data, user=test_user)

    assert response.status_code == 302

    assert Location.objects.count() == 1


@pytest.mark.django_db
def test_forbidden_handle_add_location_anonymous_user(
    moscow_ru_data: LocationData, add_location: AddLocationCallable
) -> None:
    response = add_location(location_data=moscow_ru_data)

    assert Location.objects.count() == 0

    assert response.status_code == 403

    assert 'You must be logged in to add a location' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_bad_request_handle_invalide_post_data(
    test_user: 'User',
    add_location: AddLocationCallable,
) -> None:
    invalid_data: LocationInvalidData = {'invalid_data': 'Moscow'}

    response = add_location(location_data=invalid_data, user=test_user)

    assert Location.objects.count() == 0

    assert response.status_code == 400

    assert 'Invalid request' in response.content.decode('utf-8')
