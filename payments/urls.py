from django.urls import path
from .views import *


urlpatterns = [
    path("payments/advance/initiate/", initiate_advance_payment, name="initiate-advance-payment"),
    path("payments/cash/<int:booking_id>/", confirm_cash_payment, name="confirm-cash-payment"),
    path("payments/final/initiate/", initiate_final_payment, name="initiate-final-payment"),
    path("success/", payment_success, name="payment-success"),
    path("ipn/", payment_ipn, name="payment-ipn"),
    path("fail/", payment_failed, name="payment-failed"),
    path("cancel/", payment_failed,name="payment-cancel"),
    path("status/<int:payment_id>/", payment_status_detail, name="payment-status")
]