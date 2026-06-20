from django.urls import path
from .views import *

urlpatterns = [
    path("all_category/", category_list, name="all_Category"),
    path("create_category/", create_category, name="create_category"),
    path("category_modify/<int:id>/", category_modify, name="category_modify"),
    path("category_search/", category_search, name="category_search")
]