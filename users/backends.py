import logging
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpRequest

if TYPE_CHECKING:
    from .models import User

UserModel: type['User'] = get_user_model()

logger = logging.getLogger(__name__)


class UsernameOrEmailBackend(ModelBackend):
    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> Optional['User']:
        if username is None or password is None:
            return None

        normalized_login = username.strip().lower()

        try:
            user = UserModel.objects.get(
                Q(username=normalized_login) | Q(email=normalized_login)
            )
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            logger.critical(
                f'Multiple users found for login identifier: {normalized_login}.'
                'The database is in an inconsistent state.',
                exc_info=True
                )
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
