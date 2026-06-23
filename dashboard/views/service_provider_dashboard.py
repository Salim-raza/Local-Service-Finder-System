from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from accounts.permission import IsServiceProvider
from booking.models import Booking
from booking.serializers import BookingSerializers
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from time import timezone


@api_view(["GET"])
def provider_dashboard(request):
    return Response({
        "message": "welcome to service provider dashboard"
    }, status=status.HTTP_200_OK)
    

@swagger_auto_schema(
    method='GET',
    responses={200: BookingSerializers(many=True), 400: 'Bad Request'},
    operation_description="Get pending Booking"
)
@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def get_pending_booking(request):
    booking = Booking.objects.filter(service__provider=request.user, status="pending")
    serializer = BookingSerializers(booking, many=True)
    return Response({"message": "pending booking", "data": serializer.data}, status=status.HTTP_200_OK)
    
    
@swagger_auto_schema(
    method='GET',
    responses={200: BookingSerializers(many=True), 400: 'Bad Request'},
    operation_description="Get pending Booking"
)
@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def get_accept_booking(request):
    booking = Booking.objects.filter(service__provider=request.user, status="accept")
    serializer = BookingSerializers(booking, many=True)
    return Response({"message": "accept booking", "data": serializer.data}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_PATH, description="Booking ID", type=openapi.TYPE_INTEGER)
    ],
    responses={200: BookingSerializers(), 400: 'Bad Request', 404: "Booking Not Found"},
    operation_description="accept Booking"
)

@api_view(["POST"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def accept_booking(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    if booking.status != "pending":
        return Response({"message": "Booking already processed"},status=status.HTTP_400_BAD_REQUEST)
    booking.status = 'accepted'
    booking.save()
    serializer = BookingSerializers(booking)
    return Response({"message": "Booking accepted", "data": serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method="POST",
    manual_parameters=[openapi.Parameter("pk", openapi.IN_PATH, description="Booking ID", type=openapi.TYPE_INTEGER)],
    responses={200: BookingSerializers(), 400: "Bad Request"},
    operation_description="Reject Booking"
)
@api_view(["POST"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'pending':
        booking.status == 'rejected'
        booking.save(user=request.user)
        serializer = BookingSerializers(booking)
        return Response({"message": "booking reject successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"details": "only pending booking"}, status=status.HTTP_404_NOT_FOUND)




@swagger_auto_schema(
    method='POST',
    manual_parameters=[
        openapi.Parameter('pk', openapi.IN_PATH, description="Booking ID", type=openapi.TYPE_INTEGER)
    ],
    responses={200: BookingSerializers(), 400: 'Bad Request'},
    operation_description="Complete Booking"
)
@api_view(["POST"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def complete_booking(request, pk):
    booking = Booking.objects.get(id=pk, service__provider=request.user)
    if booking.status == Booking.Status.COMPLETED:
        return Response({"message": "Already completed"},status=status.HTTP_400_BAD_REQUEST)

    booking.status == Booking.Status.COMPLETED
    booking.completed_time = timezone.now()
    booking.save()
    serializers = BookingSerializers(booking)
    return Response({"message": "Booking completed", "data": serializers.data}, status=status.HTTP_200_OK)