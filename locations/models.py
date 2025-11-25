from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Location(models.Model):
    name = models.CharField('name', max_length=255)
    country_code = models.CharField('country_code', max_length=2)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='locations')
    latitude = models.DecimalField(
        'latitude',
        max_digits=9,
        decimal_places=7,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        'longitude',
        max_digits=10,
        decimal_places=7,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    geo_key = models.CharField('geo_key', max_length=64, db_index=True, unique=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.country_code})'

    @staticmethod
    def generate_geo_key(latitude: Decimal, longitude: Decimal) -> str:
        r_latitude = latitude.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        r_longitude = longitude.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        return f'{r_latitude}:{r_longitude}'

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.geo_key = self.generate_geo_key(
            latitude=self.latitude, longitude=self.longitude
        )
        super().save(*args, **kwargs)
