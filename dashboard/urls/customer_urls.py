from ..views.customer_dashboard import customer_dashboard
from django.urls import path

urlpatterns = [
    path("customer/", customer_dashboard, name="customer_dashboard")
]
