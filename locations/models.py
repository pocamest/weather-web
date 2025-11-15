from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Location(models.Model):
    name = models.CharField('name', max_length=255)
    country_code = models.CharField('country_code', max_length=2)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='locations')
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['latitude', 'longitude'], name='unique_latitude_longitude'
            )
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.country_code})'
