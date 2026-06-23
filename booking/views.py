from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.permission import IsCustomer, IsServiceProvider
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from drf_yasg import openapi
from .serializers import *
from .models import *

# Create your views here.
@swagger_auto_schema(
    method='POST',
    request_body=BookingSerializers,
    responses={201: BookingSerializers(), 400: 'Bad Request'},
    operation_description="Service Create"
)

@api_view(["POST"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def book_service(request):
    serializers = BookingSerializers(data=request.data)
    serializers.is_valid(raise_exception=True)
    serializers.save(user=request.user)
    return Response({"message": "service book successful", "data": serializers.data}, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='PATCH',
    request_body=BookingSerializers,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description="Booking ID", type=openapi.TYPE_INTEGER)
    ],
    responses={200: BookingSerializers(), 400: 'Bad Request'},
    operation_description="Update Booking"
)
@api_view(["PATCH"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def update_booking(request, pk):
    booking = Booking.objects.get(pk=pk, user=request.user)
    if booking.status == "pending":
        serializer = BookingUpdateSerializers(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"message": "booking update successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Only pending booking can be updated"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method="post",
    manual_parameters=[
        openapi.Parameter(
        "pk",
        openapi.IN_PATH,
        description="service id",
        type=openapi.TYPE_INTEGER
        
        )
    ],
    request_body=BookingSerializers,
    responses={200: BookingSerializers(), 400: "bad request"},
    operation_description="booking cancel"
)
@api_view(["POST"])
@permission_classes([IsCustomer])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser, FormParser])
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == "pending":
        booking.status == "cancelled"
        booking.save(user=request.user)
        return Response({"message": "booking cancelled"}, status=status.HTTP_200_OK)
    return Response({"message": "only pending service cancelled"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='GET',
    responses={200: BookingSerializers(many=True), 400: 'Bad Request'},
    operation_description="Get All Booking"
)
@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def get_all_booking(request):
    booking = Booking.objects.filter(service__provider=request.user)
    serializers = BookingSerializers(booking, many=True)
    return Response({"message": "All booking", "data": serializers.data}, status=status.HTTP_200_OK)