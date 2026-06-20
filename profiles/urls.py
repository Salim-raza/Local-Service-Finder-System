from django.urls import path
from .views import *



urlpatterns = [
    path('get_all_profile/', get_all_profiles, name='get_all_profiles'),
    path('get_profile/', get_profile, name='get_profile'),
    path('modify_profile/', modify_profile, name='modify_profile'),
    path('search/', search_profile, name='search_profile'),
   ]