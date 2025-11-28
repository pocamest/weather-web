import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from .clients import OpenWeatherClient
from .exceptions import APIError
from .services import LocationService

logger = logging.getLogger(__name__)


class LocationSearchView(View):
    template_name = 'locations/search.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        query = request.GET.get('query')
        if not query:
            return render(
                request=request,
                template_name=self.template_name,
                context={'search_results': [], 'query': ''},
            )

        weather_client = OpenWeatherClient()
        location_service = LocationService(weather_client=weather_client)

        user = request.user

        search_results = []
        message_error = None
        try:
            search_results = location_service.search(query=query, user=user)
        except APIError:
            logger.exception("API call failed")
            message_error = 'Connection error, please try again later'
        context = {
            'search_results': search_results,
            'query': query,
            'message_error': message_error,
        }

        return render(
            request=request, template_name=self.template_name, context=context
        )
