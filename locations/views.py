import logging
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from users.mixins import LoginRequired403Mixin

from .clients import OpenWeatherClient
from .constants import (
    LOG_MSG_API_ERROR,
    MSG_ADD_LOCATION_BAD_REQUEST,
    MSG_WEATHER_API_CONNECTION_ERROR,
)
from .exceptions import APIError
from .forms import LocationAddForm, LocationSearchForm
from .services import LocationService

logger = logging.getLogger(__name__)


class LocationSearchView(View):
    form_class = LocationSearchForm
    template_name = 'locations/search.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        search_results = []

        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                weather_client = OpenWeatherClient()
                location_service = LocationService(weather_client=weather_client)

                query = form.cleaned_data['query']
                try:
                    search_results = location_service.search(
                        query=query, user=request.user
                    )
                except APIError:
                    logger.exception(LOG_MSG_API_ERROR)
                    messages.error(request, MSG_WEATHER_API_CONNECTION_ERROR)
        else:
            form = self.form_class()

        context = {
            'search_results': search_results,
            'form': form,
        }

        return render(
            request=request, template_name=self.template_name, context=context
        )


class LocationAddView(LoginRequired403Mixin, View):
    form_class = LocationAddForm

    def post(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        assert user.is_authenticated

        form = self.form_class(request.POST)
        if form.is_valid():
            weather_client = OpenWeatherClient()
            location_service = LocationService(weather_client=weather_client)
            location_service.add(user, **form.cleaned_data)
            return redirect(settings.ADD_LOCATION_REDIRECT_URL)

        logger.error(f'Failed to add location: {form.errors}')
        return HttpResponseBadRequest(MSG_ADD_LOCATION_BAD_REQUEST)


class LocationListView(View):
    template_name = 'locations/list.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        context: dict[str, Any] = {'locations_with_weather': [], 'page_obj': None}
        if not user.is_authenticated:
            return render(
                request=request, template_name=self.template_name, context=context
            )

        user_locations = user.locations.order_by('name')

        if not user_locations.exists():
            return render(
                request=request, template_name=self.template_name, context=context
            )

        paginator = Paginator(
            object_list=user_locations, per_page=settings.LOCATIONS_PER_PAGE
        )

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        weather_client = OpenWeatherClient()
        location_service = LocationService(weather_client=weather_client)

        locations_with_weather = location_service.get_locations_with_weather(
            page_obj.object_list
        )

        context = {
            'locations_with_weather': locations_with_weather,
            'page_obj': page_obj,
        }

        return render(
            request=request, template_name=self.template_name, context=context
        )


class LocationDeleteView(LoginRequired403Mixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        user = request.user
        assert user.is_authenticated

        location = get_object_or_404(user.locations, id=pk)
        user.locations.remove(location)

        return redirect(settings.DELETE_LOCATION_REDIRECT_URL)
