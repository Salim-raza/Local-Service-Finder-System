from ..views.service_provider_dashboard import provider_dashboard
from django.urls import path

urlpatterns = [
    path("service_provide/", provider_dashboard, name="provider_dashboard")
]
