from django.urls import path
from .views import *


urlpatterns = [
    path("service_book/", book_service, name="book_service"),
    path("get_all_booking/", get_all_booking, name="get_all_booking"),
    path("booking_update/<int:pk>/", update_booking, name="update_booking"),
    path("cancel_booking/", cancel_booking, name="cancel_booking")
]
