from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from .forms import RegistrationForm

if TYPE_CHECKING:
    from .models import User

UserModel: type['User'] = get_user_model()


@pytest.mark.django_db
def test_successful_registration(client: Client) -> None:
    user_data = {
        'username': 'Test_user',
        'email': 'TESTUSER@EXAMPLE.com',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }
    url_registration = reverse('users:register')
    response = client.post(path=url_registration, data=user_data)

    assertRedirects(
        response=response, expected_url=str(settings.REGISTRATION_REDIRECT_URL)
    )

    assert UserModel.objects.count() == 1
    created_user = UserModel.objects.first()
    assert created_user is not None
    assert created_user.username == 'test_user'
    assert created_user.email == 'testuser@example.com'


@pytest.mark.django_db
def test_registration_with_invalid_username(client: Client) -> None:
    user_data = {
        'username': 'test@user',
        'email': 'testuser@example.com',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

    url_registration = reverse('users:register')
    response = client.post(path=url_registration, data=user_data)

    assert UserModel.objects.count() == 0
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field='username', code='invalid_username')


@pytest.mark.django_db
def test_registration_with_duplicate_username(client: Client) -> None:
    UserModel.objects.create_user(
        username='TestUser', email='testuser@example.com', password='testpassword'
    )
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

    url_registration = reverse('users:register')
    response = client.post(path=url_registration, data=user_data)

    assert UserModel.objects.count() == 1
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field='username', code='duplicate_username')


@pytest.mark.django_db
def test_registration_with_duplicate_email(client: Client) -> None:
    UserModel.objects.create_user(
        username='testuser', email='testuser@example.com', password='testpassword'
    )
    user_data = {
        'username': 'testuser1',
        'email': 'testuser@example.com',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }

    url_registration = reverse('users:register')
    response = client.post(path=url_registration, data=user_data)

    assert UserModel.objects.count() == 1
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field='email', code='duplicate_email')
