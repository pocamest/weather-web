import logging

from django.conf import settings
from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import redirect, render
from django.views import View

from .clients import OpenWeatherClient
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
                    logger.exception('API call failed')
                    messages.error(request, 'Connection error, please try again later')
        else:
            form = self.form_class()

        context = {
            'search_results': search_results,
            'form': form,
        }

        return render(
            request=request, template_name=self.template_name, context=context
        )


class LocationAddView(View):
    form_class = LocationAddForm

    def post(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden('You must be logged in to add a location')
        form = self.form_class(request.POST)
        if form.is_valid():
            weather_client = OpenWeatherClient()
            location_service = LocationService(weather_client=weather_client)
            location_service.add(user, **form.cleaned_data)
            return redirect(settings.ADD_LOCATION_REDIRECT_URL)

        logger.error(f'Failed to add location: {form.errors}')
        return HttpResponseBadRequest('Invalid request')
