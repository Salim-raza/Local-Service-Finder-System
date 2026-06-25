from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("signin/", signin, name="signin"),
    path("change_password/", change_password, name="change_password"),
    path("send_otp/", send_otp, name="send_otp"),
    path("reset_password/", rest_password, name="reset_password"),
    path("signout/", signout, name="signout"),
]
