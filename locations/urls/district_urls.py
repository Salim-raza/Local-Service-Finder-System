from django.urls import path
from views.district_views import *

urlpatterns = [
    path("create_district/", create_district, name="create_district"),
    path("update_district/<int:pk>/", update_district, name="update_district"),
    path("delete_district/<int:pk>/", delete_district, name="delete_district")
]
