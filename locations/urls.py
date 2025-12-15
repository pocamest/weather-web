from django.urls import path

from .views import LocationAddView, LocationListView, LocationSearchView

app_name = 'locations'
urlpatterns = [
    path('search/', LocationSearchView.as_view(), name='search'),
    path('add/', LocationAddView.as_view(), name='add'),
    path('', LocationListView.as_view(), name='list'),
]
