from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from booking.serializers import BookingSerializers
from accounts.permission import IsServiceProvider
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.core.mail import send_mail
from booking.models import Booking
from django.utils import timezone
from rest_framework import status
from django.conf import settings
from drf_yasg import openapi


@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
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
    booking = Booking.objects.filter(
        service__provider=request.user,
        status=Booking.Status.ACCEPTED,
    )
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
    booking = get_object_or_404(Booking, id=pk, service__provider=request.user)
    if booking.status != Booking.Status.PENDING:
        return Response({"message": "Booking already processed"},status=status.HTTP_400_BAD_REQUEST)
    booking.status = Booking.Status.ACCEPTED
    booking.save()
    serializer = BookingSerializers(booking)
    send_mail(
        subject="you booking accept",
        message=f"""
        hello {booking.user.first_name}
        
        your booking request accepted service provider 
        
        Booking id : {booking.id}
        thanks you
        Customer Support Team
        """,
        
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[booking.user.email],
        fail_silently=False
    )
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
    booking = get_object_or_404(Booking, pk=pk, service__provider=request.user)
    if booking.status == Booking.Status.PENDING:
        booking.status = Booking.Status.REJECTED
        booking.save()
        serializer = BookingSerializers(booking)
        send_mail(
            subject="you booking rejected",
            message=f"""
            Hello {booking.user.first_name},

            We are sorry to inform you that your booking request has been rejected.

            Booking ID: {booking.id}

            Please feel free to submit another booking request or contact our support team if you have any questions.

            Thank you for choosing our service.

            Regards,
            Customer Support Team
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[booking.user.email],
            fail_silently=False
        )
        return Response({"message": "booking reject successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"details": "only pending booking"}, status=status.HTTP_400_BAD_REQUEST)




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
    booking = get_object_or_404(Booking, id=pk, service__provider=request.user)
    if booking.status != Booking.Status.ACCEPTED:
        return Response(
            {"message": "Only accepted bookings can be completed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    booking.status = Booking.Status.COMPLETED
    booking.completed_time = timezone.now()
    booking.save()
    serializers = BookingSerializers(booking)
    return Response({"message": "Booking completed", "data": serializers.data}, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method="GET",
    response={200: "total accept booking"},
    operation_description="total accept booking"
)
@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def total_accept_booking(request):
    booking = Booking.objects.filter(service__provider=request.user, status="accepted").count()
    return Response(booking, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method="GET",
    response={200: "total completed booking"},
    operation_description="total completed booking"
)
@api_view(["GET"])
@permission_classes([IsServiceProvider])
@authentication_classes([JWTAuthentication])
def total_completed_booking(request):
    booking = Booking.objects.filter(service__provider=request.user, status="completed").count()
    return Response(booking, status=status.HTTP_200_OK)