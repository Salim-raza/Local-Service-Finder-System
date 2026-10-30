from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.permission import IsCustomer, IsServiceProvider
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from drf_yasg import openapi
from .serializers import *
from .models import *

# Create your views here.
@swagger_auto_schema(
    method='POST',
    request_body=BookingSerializers,
    responses={201: BookingSerializers(), 400: 'Bad Request'},
    manual_parameters=[
        openapi.Parameter(
            "booking_date", openapi.IN_FORM,
            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
            description="YYYY-MM-DD", default="2026-10-15"
        ),
        openapi.Parameter(
            "booking_time", openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            description="HH:MM (24-hour)", default="14:30"
        ),
    ],
    operation_description="booking Create"
)
@api_view(["POST"])
@permission_classes([IsCustomer])
@parser_classes([MultiPartParser, FormParser])
@authentication_classes([JWTAuthentication])
def book_service(request):
    serializer = BookingSerializers(data=request.data)
    serializer.is_valid(raise_exception=True)

    service = serializer.validated_data["service"]

    if not service.is_active:
        return Response(
            {"error": "This service is not available."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if service.pricing_type == Service.PricingType.FIXED:
        price = service.base_price

    elif service.pricing_type == Service.PricingType.HOURLY:
        return Response(
            {
                "error": (
                    "Hourly booking requires duration to calculate "
                    "the total price."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    else:
        return Response(
            {
                "error": (
                    "This service requires a quotation before booking."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if price is None or price <= 0:
        return Response(
            {"error": "Service price is not configured correctly."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Calculate mandatory 20% advance
    advance_amount = (
        price * Decimal("0.20")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    booking = serializer.save(
        user=request.user,
        price_at_booking=price,
        advance_amount=advance_amount,
        paid_amount=Decimal("0.00"),
        payment_status=Booking.PaymentStatus.UNPAID,
    )

    try:
        send_mail(
            subject="Booking Confirmation",
            message=f"""
            Dear {request.user.first_name},

            Your booking request has been submitted successfully.

            Booking ID: {booking.id}
            Service: {service.name}
            Total Price: {booking.price_at_booking} BDT
            Advance Amount (20%): {booking.advance_amount} BDT

            The service provider will review your booking request.

            Thank you for choosing our platform.
            Best Regards,
            Customer Support Team
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
    except Exception:
        # Booking has already been created; don't return a false booking failure.
        pass

    return Response(
        {
            "message": "Service booking successful.",
            "data": BookingSerializers(booking).data,
        },
        status=status.HTTP_201_CREATED,
    )

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
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == "pending":
        serializer = BookingUpdateSerializers(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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
        booking.status = Booking.Status.CANCELLED
        booking.cancelled_by = request.user
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = request.data.get("cancellation_reason", "")
        booking.save()
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