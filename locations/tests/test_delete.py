from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects

from users.constants import MSG_LOGIN_REQUIRED_FORBIDDEN

from .test_types import CreateLocationCallable, LocationData

if TYPE_CHECKING:
    from users.models import User

UserModel: type['User'] = get_user_model()


@pytest.mark.django_db
def test_successful_delete_location(
    moscow_ru_data: LocationData,
    create_location: CreateLocationCallable,
    test_user: 'User',
    client: Client,
) -> None:
    location = create_location(location_data=moscow_ru_data, user=test_user)

    client.force_login(test_user)
    delete_url = reverse(viewname='locations:delete', args=[location.id])
    response = client.post(delete_url)

    assert test_user.locations.count() == 0
    assertRedirects(
        response=response, expected_url=reverse(settings.DELETE_LOCATION_REDIRECT_URL)
    )


@pytest.mark.django_db
def test_delete_non_existent_location_is_not_found(
    test_user: 'User',
    client: Client,
) -> None:
    client.force_login(test_user)
    delete_url = reverse(viewname='locations:delete', args=[1])
    response = client.post(delete_url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_not_owner_location_is_not_found(
    moscow_ru_data: LocationData,
    test_user: 'User',
    create_location: CreateLocationCallable,
    client: Client,
) -> None:
    owner = UserModel.objects.create_user(
        username='owner', email='owner@example.com', password='ownerpassword'
    )

    owner_location = create_location(location_data=moscow_ru_data, user=owner)

    client.force_login(test_user)
    delete_url = reverse(viewname='locations:delete', args=[owner_location.id])
    response = client.post(delete_url)

    assert response.status_code == 404
    assert owner.locations.count() == 1


@pytest.mark.django_db
def test_delete_location_is_forbidden_for_anonymous_user(client: Client) -> None:
    delete_url = reverse(viewname='locations:delete', args=[1])
    response = client.post(path=delete_url)

    assertContains(
        response=response, text=MSG_LOGIN_REQUIRED_FORBIDDEN, status_code=403
    )
