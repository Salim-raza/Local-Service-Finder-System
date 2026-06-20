from django.urls import path
from .views import *


urlpatterns = [
    path("review/", create_review_rating, name="create_review_rating"),
    path("update_review/", update_review_rating, name="update_review_rating"),
    path("delete_review/", delete_review_rating, name="delete_review_rating"),
    path("get_review/<int:service_id>/", get_review, name="get_review"),
    path("get_average_review_rating/<int:service_id>/", get_average_review_rating, name="get_average_review_rating"),
]
