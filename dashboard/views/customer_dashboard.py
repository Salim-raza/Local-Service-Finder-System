from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permission import IsCustomer
from rest_framework import status
from rest_framework.response import Response


@api_view(["GET"])
def customer_dashboard(request):
    return Response({
        "message": "welcome to customer dashboard"
    }, status=status.HTTP_200_OK)