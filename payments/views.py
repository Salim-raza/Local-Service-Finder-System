from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permission import IsCustomer, IsServiceProvider
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from decimal import Decimal, ROUND_HALF_UP
from sslcommerz_lib import SSLCOMMERZ
from booking.models import Booking
from django.db import transaction
from rest_framework import status
from django.conf import settings
from drf_yasg import openapi
from .models import Payment
from decimal import Decimal

# Create your views here.
@transaction.atomic
def verify_payment_transaction(tran_id, val_id):
    payment = Payment.objects.select_for_update().filter(
        transaction_id=tran_id
    ).first()

    if payment is None:
        return False, "Payment not found."

    if payment.status == Payment.Status.SUCCESS:
        return True, "Payment already verified."

    if payment.status != Payment.Status.PENDING:
        return False, "Payment is not pending."

    sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)
    result = sslcz.validationTransactionOrder(val_id)

    if not isinstance(result, dict):
        return False, "Invalid validation response."

    if (
        result.get("status") not in ["VALID", "VALIDATED"]
        or result.get("tran_id") != str(payment.transaction_id)
        or result.get("currency") != "BDT"
        or result.get("amount") is None
        or Decimal(str(result["amount"])) != payment.amount
    ):
        return False, "Transaction validation failed."

    booking = Booking.objects.select_for_update().get(
        pk=payment.booking_id
    )

    if payment.purpose == Payment.Purpose.ADVANCE:
        if booking.paid_amount != 0:
            return False, "Advance was already recorded."

        if payment.amount != booking.advance_amount:
            return False, "Advance amount mismatch."

    elif payment.purpose == Payment.Purpose.FINAL:
        if booking.status != Booking.Status.COMPLETED:
            return False, "Booking is not completed."

        if payment.amount != booking.price_at_booking - booking.paid_amount:
            return False, "Final amount mismatch."

    if booking.paid_amount + payment.amount > booking.price_at_booking:
        return False, "Payment exceeds booking total."

    payment.status = Payment.Status.SUCCESS
    payment.sslcommerz_val_id = val_id
    payment.save(update_fields=["status", "sslcommerz_val_id"])

    booking.paid_amount += payment.amount

    if booking.paid_amount >= booking.price_at_booking:
        booking.paid_amount = booking.price_at_booking
        booking.payment_status = Booking.PaymentStatus.PAID
    else:
        booking.payment_status = Booking.PaymentStatus.PARTIALLY_PAID

    booking.save(update_fields=[
        "paid_amount",
        "payment_status",
        "updated_at",
    ])

    return True, "Payment verified successfully."



def create_payment_session(payment, request):
    booking = payment.booking
    profile = getattr(booking.user, "profile", None)

    sslcz = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS)

    post_body = {
        "total_amount": str(payment.amount),
        "currency": "BDT",
        "tran_id": str(payment.transaction_id),
        "success_url": request.build_absolute_uri(
            "/api/v1/payments/success/"
        ),
        "fail_url": request.build_absolute_uri(
            "/api/v1/payments/fail/"
        ),
        "cancel_url": request.build_absolute_uri(
            "/api/v1/payments/cancel/"
        ),
        "ipn_url": request.build_absolute_uri(
            "/api/v1/payments/ipn/"
        ),
        "emi_option": 0,
        "cus_name": booking.user.get_full_name() or booking.user.email,
        "cus_email": booking.user.email,
        "cus_phone": getattr(profile, "phone", "") or "01700000000",
        "cus_add1": getattr(profile, "area", "") or "Bangladesh",
        "cus_city": getattr(profile, "city", "") or "Dhaka",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "num_of_item": 1,
        "product_name": f"Booking {booking.id} {payment.purpose}",
        "product_category": "Service",
        "product_profile": "general",
    }

    result = sslcz.createSession(post_body)
    gateway_url = result.get("GatewayPageURL")

    if not gateway_url:
        raise ValueError("SSLCommerz did not return GatewayPageURL.")

    return gateway_url


@swagger_auto_schema(
    method="post",
    operation_summary="Initiate Advance Payment",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["booking_id"],
        properties={
            "booking_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Booking ID",
            ),
        },
    ),
    responses={
        201: "Payment initiated successfully",
        400: "Invalid booking",
        409: "Payment already pending",
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsCustomer])
def initiate_advance_payment(request):
    booking_id = request.data.get("booking_id")

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            id=booking_id,
            user=request.user,
        )

        if booking.status in [
            Booking.Status.REJECTED,
            Booking.Status.CANCELLED,
        ]:
            return Response(
                {"error": "Booking cannot be paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.paid_amount > 0:
            return Response(
                {"error": "Advance has already been paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Payment.objects.filter(
            booking=booking,
            purpose=Payment.Purpose.ADVANCE,
            status=Payment.Status.PENDING,
        ).exists():
            return Response(
                {"error": "An advance payment attempt is already pending."},
                status=status.HTTP_409_CONFLICT,
            )

        payment = Payment.objects.create(
            booking=booking,
            purpose=Payment.Purpose.ADVANCE,
            amount=booking.advance_amount,
        )

    try:
        gateway_url = create_payment_session(payment, request)
    except Exception:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return Response(
            {"error": "Could not initiate SSLCommerz payment."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({
        "payment_id": payment.id,
        "amount": str(payment.amount),
        "gateway_url": gateway_url,
    }, status=status.HTTP_201_CREATED)



@swagger_auto_schema(
    method="post",
    operation_summary="Initiate Final Online Payment",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["booking_id"],
        properties={
            "booking_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Completed booking ID",
            ),
        },
    ),
    responses={
        201: "Payment initiated successfully",
        400: "Invalid booking or payment method",
        409: "Payment already pending",
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsCustomer])
def initiate_final_payment(request):
    booking_id = request.data.get("booking_id")

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            id=booking_id,
            user=request.user,
        )

        if booking.status != Booking.Status.COMPLETED:
            return Response(
                {"error": "Service must be completed first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.final_payment_method != Booking.FinalPaymentMethod.ONLINE:
            return Response(
                {"error": "Final payment method must be online."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = booking.price_at_booking - booking.paid_amount

        if remaining <= 0:
            return Response(
                {"error": "Booking is already fully paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Payment.objects.filter(
            booking=booking,
            purpose=Payment.Purpose.FINAL,
            status=Payment.Status.PENDING,
        ).exists():
            return Response(
                {"error": "A final payment attempt is already pending."},
                status=status.HTTP_409_CONFLICT,
            )

        payment = Payment.objects.create(
            booking=booking,
            purpose=Payment.Purpose.FINAL,
            amount=remaining,
        )

    try:
        gateway_url = create_payment_session(payment, request)
    except Exception:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        return Response(
            {"error": "Could not initiate SSLCommerz payment."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response({
        "payment_id": payment.id,
        "amount": str(payment.amount),
        "gateway_url": gateway_url,
    }, status=status.HTTP_201_CREATED)
    
    
@swagger_auto_schema(
    method="post",
    operation_summary="SSLCommerz Payment Success Callback",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id", "val_id"],
        properties={
            "tran_id": openapi.Schema(type=openapi.TYPE_STRING),
            "val_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: "Payment verified",
        400: "Verification failed",
        502: "Verification unavailable",
    },
)    
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_success(request):
    tran_id = request.data.get("tran_id")
    val_id = request.data.get("val_id")

    if not tran_id or not val_id:
        return Response(
            {"error": "Missing transaction details."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        success, message = verify_payment_transaction(tran_id, val_id)
    except Exception:
        return Response(
            {"error": "Payment verification is temporarily unavailable."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not success:
        return Response(
            {"error": message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"message": message})





@swagger_auto_schema(
    method="post",
    operation_summary="SSLCommerz IPN Callback",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id", "val_id"],
        properties={
            "tran_id": openapi.Schema(type=openapi.TYPE_STRING),
            "val_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: "IPN processed",
        400: "Invalid transaction",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_ipn(request):
    tran_id = request.data.get("tran_id")
    val_id = request.data.get("val_id")

    if not tran_id or not val_id:
        return Response(
            {"error": "Missing transaction details."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        success, message = verify_payment_transaction(tran_id, val_id)
    except Exception:
        return Response(
            {"error": "Verification failed."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if not success:
        return Response(
            {"error": message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"message": message})



@swagger_auto_schema(
    method="post",
    operation_summary="Confirm Cash Payment",
    responses={
        200: "Cash payment confirmed",
        400: "Invalid booking or payment method",
        404: "Booking not found",
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsServiceProvider])
def confirm_cash_payment(request, booking_id):
    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(),
            id=booking_id,
            service__provider=request.user,
        )

        if booking.status != Booking.Status.COMPLETED:
            return Response(
                {"error": "Service must be completed first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking.final_payment_method != Booking.FinalPaymentMethod.CASH:
            return Response(
                {"error": "Final payment method is not cash."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = booking.price_at_booking - booking.paid_amount

        if remaining <= 0:
            return Response(
                {"error": "Booking is already fully paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.paid_amount += remaining
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.save(update_fields=[
            "paid_amount",
            "payment_status",
            "updated_at",
        ])

    return Response({
        "message": "Cash payment confirmed.",
        "paid_amount": str(booking.paid_amount),
        "remaining_amount": str(booking.remaining_amount),
    })
    
    
@swagger_auto_schema(
    method="post",
    operation_summary="Payment Failed or Cancelled",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id"],
        properties={
            "tran_id": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: "Payment status updated",
        400: "Missing transaction ID",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_failed(request):
    tran_id = request.data.get("tran_id")

    if not tran_id:
        return Response(
            {"error": "Missing transaction ID."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    updated = Payment.objects.filter(
        transaction_id=tran_id,
        status=Payment.Status.PENDING,
    ).update(status=Payment.Status.FAILED)

    return Response({
        "message": "Payment failure processed.",
        "updated": bool(updated),
    })
