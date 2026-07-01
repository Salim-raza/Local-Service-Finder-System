from ..views.admin_dashboard import *
from django.urls import path


urlpatterns = [
    path("admin/", admin_panel, name="admin_panel"),
    path("account_activate/<int:pk>/", pending_account_active, name="account_activate"),
    path("pending_account/", pending_account_list, name="pending_account"),
    path("total_activate_account_count/", total_activate_account_count, name="total_activate_account_count"),
    path("total_activate_pending_count/", total_activate_pending_count, name="total_activate_pending_count")
]