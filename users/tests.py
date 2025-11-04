from collections.abc import Callable
from typing import TYPE_CHECKING, NotRequired, TypedDict, Unpack

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import NON_FIELD_ERRORS
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from .forms import RegistrationForm

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse as DjangoTestResponse

    from .models import User
else:
    DjangoTestResponse = HttpResponse

UserModel: type['User'] = get_user_model()


class UserRegistrationData(TypedDict):
    username: str
    email: str
    password1: str
    password2: str


class UserRegistrationParams(TypedDict):
    username: NotRequired[str]
    email: NotRequired[str]
    password1: NotRequired[str]
    password2: NotRequired[str]


RegisterUserCallable = Callable[[Unpack[UserRegistrationParams]], DjangoTestResponse]


@pytest.fixture
def register_user(
    client: Client,
) -> RegisterUserCallable:
    def _register_user(**kwargs: Unpack[UserRegistrationParams]) -> DjangoTestResponse:
        user_data: UserRegistrationData = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        user_data.update(kwargs)
        url_registration = reverse('users:register')
        return client.post(path=url_registration, data=user_data)

    return _register_user


@pytest.mark.django_db
def test_successful_registration_normalizes_case(
    register_user: RegisterUserCallable,
) -> None:
    response = register_user(username='TestUser', email='TestUser@example.com')
    assertRedirects(
        response=response, expected_url=str(settings.REGISTRATION_REDIRECT_URL)
    )
    assert UserModel.objects.count() == 1
    created_user = UserModel.objects.first()
    assert created_user is not None
    assert created_user.username == 'testuser'
    assert created_user.email == 'testuser@example.com'


@pytest.mark.django_db
def test_registration_with_invalid_username(
    register_user: RegisterUserCallable,
) -> None:
    response = register_user(username='test@user')
    assert UserModel.objects.count() == 0
    assert response.status_code == 200
    form: RegistrationForm = response.context['form']

    assert form.has_error(field='username', code='invalid_username')


@pytest.mark.django_db
def test_registration_with_duplicate_username(
    register_user: RegisterUserCallable,
) -> None:
    UserModel.objects.create_user(
        username='testuser', email='another@example.com', password='testpassword'
    )
    response = register_user(username='TestUser')

    assert UserModel.objects.count() == 1
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field='username', code='duplicate_username')


@pytest.mark.django_db
def test_registration_with_duplicate_email(
    register_user: RegisterUserCallable,
) -> None:
    UserModel.objects.create_user(
        username='anotheruser', email='testuser@example.com', password='testpassword'
    )
    response = register_user(email='TestUser@example.com')

    assert UserModel.objects.count() == 1
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field='email', code='duplicate_email')


@pytest.mark.django_db
def test_registration_with_different_passwords(
    register_user: RegisterUserCallable,
) -> None:
    response = register_user(password1='testpassword1', password2='testpassword2')

    assert UserModel.objects.count() == 0
    assert response.status_code == 200

    form: RegistrationForm = response.context['form']

    assert form.has_error(field=NON_FIELD_ERRORS, code='different_passwords')
