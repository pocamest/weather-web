from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models.functions import Lower


class UserManager(DjangoUserManager['User']):
    def create_user(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> 'User':
        if not email:
            raise ValueError('An email address must be provided.')

        normalize_username = username.strip().lower()
        normalize_email = email.strip().lower()
        return super().create_user(
            username=normalize_username,
            email=normalize_email,
            password=password,
            **extra_fields,
        )

    def create_superuser(
        self,
        username: str,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: Any,
    ) -> 'User':
        if not email:
            raise ValueError('An email address must be provided.')

        normalize_username = username.strip().lower()
        normalize_email = email.strip().lower()
        return super().create_superuser(
            username=normalize_username,
            email=normalize_email,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):
    username = models.CharField('username', max_length=150, unique=False)
    email = models.EmailField('email address', unique=False)

    objects: ClassVar[UserManager] = UserManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.username = self.username.strip().lower()
        self.email = self.email.strip().lower()

        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('username'), name='unique_lower_username'),
            models.UniqueConstraint(Lower('email'), name='unique_lower_email'),
        ]
