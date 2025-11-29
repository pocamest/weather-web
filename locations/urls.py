from django.urls import path

from .views import LocationSearchView

app_name = 'locations'
urlpatterns = [
    path('search/', LocationSearchView.as_view(), name='search'),
]
