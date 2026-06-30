from ..views.service_provider_dashboard import *
from django.urls import path

urlpatterns = [
    path("service_provide/", provider_dashboard, name="provider_dashboard"),
    path("get_pending_booking/", get_pending_booking, name="get_pending_booking"),
    path("get_accept_booking/", get_accept_booking, name="get_accept_booking"),
    path("accept_booking/<int:pk>/", accept_booking, name="accept_booking"),
    path("reject_booking/<int:pk>/", reject_booking, name="reject_booking"),
    path("complete_booking/<int:pk>/", complete_booking, name="complete_booking"),
    path("total_accept_booking/", total_accept_booking, name="total_accept_booking"),
    path("total_completed_booking/", total_completed_booking, name="total_completed_booking")
]
