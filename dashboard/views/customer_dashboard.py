from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.serializers import UserCreateSerializers
from booking.serializers import BookingSerializers
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from accounts.permission import IsCustomer
from booking.models import Booking
from rest_framework import status


@api_view(["GET"])
def customer_dashboard(request):
    return Response({
        "message": "welcome to customer dashboard"
    }, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(
    method="get",
    responses={200: UserCreateSerializers(many=True), 400: "Bad Request"},
    operation_description="get all oder"
)
@api_view(["GET"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
def total_oder_list(request):
    booking = Booking.objects.filter(user=request.user)
    serializer = BookingSerializers(booking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
@swagger_auto_schema(
    method="get",
    responses={200: UserCreateSerializers(many=True), 400: "Bad Request"},
    operation_description="get all completed a oder"
)
@api_view(["GET"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
def completed_booking(request):
    booking = Booking.objects.filter(user=request.user, status="completed")
    serializer = BookingSerializers(booking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
@swagger_auto_schema(
    method="get",
    responses={200: UserCreateSerializers(many=True), 400: "Bad Request"},
    operation_description="get all pending account"
)
@api_view(["GET"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
def pending_booking(request):
    booking = Booking.objects.filter(user=request.user, status="pending")
    serializer = BookingSerializers(booking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    