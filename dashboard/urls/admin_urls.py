from ..views.admin_dashboard import admin_panel
from django.urls import path


urlpatterns = [
    path("admin/", admin_panel, name="admin_panel")
]