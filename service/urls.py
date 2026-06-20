from django.urls import path
from .views import *


urlpatterns = [
    path("all_service/", all_service, name="all_service"),
    path("services/", service, name="service"),
    path("service_modify/<int:id>/", service_modify, name="service_modify"),
    path("search_service/", search_service, name="search_service"),
]
