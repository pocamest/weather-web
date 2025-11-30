import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from .clients import OpenWeatherClient
from .exceptions import APIError
from .forms import LocationSearchForm
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
                    form.add_error(None, 'Connection error, please try again later')
        else:
            form = self.form_class()

        context = {
            'search_results': search_results,
            'form': form,
        }

        return render(
            request=request, template_name=self.template_name, context=context
        )
