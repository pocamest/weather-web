from typing import Any

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

from .constants import MSG_ANONYMOUS_REQUIRED_FORBIDDEN, MSG_LOGIN_REQUIRED_FORBIDDEN


class LoginRequiredForbiddenMixin:
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseForbidden(MSG_LOGIN_REQUIRED_FORBIDDEN)

        return super().dispatch(request, *args, **kwargs)  # type: ignore[no-any-return, misc]


class AnonymousRequiredForbiddenMixin:
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseForbidden(MSG_ANONYMOUS_REQUIRED_FORBIDDEN)

        return super().dispatch(request, *args, **kwargs)  # type: ignore[no-any-return, misc]
