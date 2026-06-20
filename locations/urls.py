from django.urls import path
from .views import *


urlpatterns = [
    path("create_division/", create_division, name="create_division"),
    path("update_division/<int:pk>/", update_division, name="update_division"),
    path("delete_division/<int:pk>/", delete_division, name="delete_division"),
    path("create_district/", create_district, name="create_district"),
    path("update_district/<int:pk>/", update_district, name="update_district"),
    path("delete_district/<int:pk>/", delete_district, name="delete_district"),
    path("create_upazila/", create_upazila, name="create_upazila"),
    path("update_upazila/<int:pk>/", update_upazila, name="update_upazila"),
    path("delete_upazila/<int:pk>/", delete_upazila, name="delete_upazila")
]
