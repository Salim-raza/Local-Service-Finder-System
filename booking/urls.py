from django.urls import path
from .views import *


urlpatterns = [
    path("service_book/", book_service, name="book_service"),
    path("accept_booking/<int:pk>/", accept_booking, name="accept_booking"),
    path("get_all_booking/", get_all_booking, name="get_all_booking"),
    path("get_pending_booking/", get_pending_booking, name="get_pending_booking"),
    path("complete_booking/<int:pk>/", complete_booking, name="complete_booking"),
    path("reject_booking/<int:pk>/", reject_booking, name="reject_booking"),
    path("booking_update/<int:pk>/", update_booking, name="update_booking")
]
