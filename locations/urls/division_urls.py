from django.urls import path
from views.division_views import *


urlpatterns = [
    path("create_division/", create_division, name="create_division"),
    path("update_division/<int:pk>/", update_division, name="update_division"),
    path("delete_division/<int:pk>/", delete_division, name="delete_division")
]
