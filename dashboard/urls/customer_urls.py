from ..views.customer_dashboard import *
from django.urls import path

urlpatterns = [
    path("customer/", customer_dashboard, name="customer_dashboard"),
    path("total_oder_list/", total_oder_list, name="total_oder_list"),
    path("completed_booking/", completed_booking, name="completed_booking"),
    path("pending_booking/", pending_booking, name="pending_booking"),
]
