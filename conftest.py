from typing import TYPE_CHECKING

import pytest
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from users.models import User

UserModel: type['User'] = get_user_model()


@pytest.fixture
def test_user_password() -> str:
    return 'testpassword'


@pytest.fixture
def test_user(db: None, test_user_password: str) -> 'User':
    return UserModel.objects.create_user(
        username='testuser', email='testuser@example.com', password=test_user_password
    )
