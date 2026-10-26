from django.urls import path
from views.upazila_views import *


urlpatterns = [
    path("create_upazila/", create_upazila, name="create_upazila"),
    path("update_upazila/<int:pk>/", update_upazila, name="update_upazila"),
    path("delete_upazila/<int:pk>/", delete_upazila, name="delete_upazila")
]
