from typing import TYPE_CHECKING

from django.http import HttpResponse

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse as DjangoTestResponse
else:
    DjangoTestResponse = HttpResponse

__all__ = ['DjangoTestResponse']
