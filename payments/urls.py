from django.urls import path
from .views import *


urlpatterns = [
    path("payments/advance/initiate/", initiate_advance_payment, name="initiate-advance-payment"),
    path("payments/cash/<int:booking_id>/", confirm_cash_payment, name="confirm-cash-payment"),
    path("payments/final/initiate/", initiate_final_payment, name="initiate-final-payment"),
    path("payments/success/", payment_success, name="payment-success"),
    path("payments/ipn/", payment_ipn, name="payment-ipn"),
    path("payments/fail/", payment_failed, name="payment-failed"),
    path("payments/cancel/", payment_failed,name="payment-cancel")
]