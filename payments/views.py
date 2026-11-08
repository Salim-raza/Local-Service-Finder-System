from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permission import IsCustomer, IsServiceProvider
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from sslcommerz_lib import SSLCOMMERZ
from booking.models import Booking
from django.db import transaction
from rest_framework import request, status
from django.conf import settings
from drf_yasg import openapi
from .models import Payment
import hashlib
import hmac

# Create your views here.
MONEY = Decimal("0.01")


def _as_money(value):
    """Convert a value to a 2-decimal Decimal without using float math."""
    return Decimal(str(value)).quantize(MONEY)


@transaction.atomic
def verify_payment_transaction(tran_id, val_id):
    """Verify with SSLCommerz and atomically record the payment once."""
    payment = (
        Payment.objects.select_for_update()
        .filter(transaction_id=tran_id)
        .first()
    )
    if payment is None:
        return False, "Payment not found."

    # Idempotency: callbacks/IPN may arrive more than once.
    if payment.status == Payment.Status.SUCCESS:
        if payment.sslcommerz_val_id and payment.sslcommerz_val_id != str(val_id):
            return False, "Validation ID does not match this payment."
        return True, "Payment already verified."

    if payment.status != Payment.Status.PENDING:
        return False, "Payment is not pending."

    try:
        result = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS).validationTransactionOrder(
            val_id
        )
    except Exception:
        # Let the callback return a retryable 502; do not change payment state.
        raise

    if not isinstance(result, dict):
        return False, "Invalid SSLCommerz validation response."

    try:
        gateway_amount = _as_money(result.get("amount"))
        expected_amount = _as_money(payment.amount)
    except (InvalidOperation, TypeError, ValueError):
        return False, "Invalid transaction amount from SSLCommerz."

    if (
        result.get("status") not in {"VALID", "VALIDATED"}
        or str(result.get("tran_id", "")) != str(payment.transaction_id)
        or str(result.get("val_id", "")) != str(val_id)
        or str(result.get("currency", "")).upper() != "BDT"
        or gateway_amount != expected_amount
    ):
        return False, "SSLCommerz transaction validation failed."

    booking = Booking.objects.select_for_update().get(pk=payment.booking_id)

    total = _as_money(booking.price_at_booking)
    paid = _as_money(booking.paid_amount)
    amount = _as_money(payment.amount)

    if total <= 0 or amount <= 0 or paid < 0 or paid > total:
        return False, "Booking payment values are invalid."

    if payment.purpose == Payment.Purpose.ADVANCE:
        if booking.status != Booking.Status.ACCEPTED:
            return False, "Booking must be accepted before advance payment."
        if paid != Decimal("0.00"):
            return False, "Advance payment has already been recorded."
        if amount != _as_money(booking.advance_amount):
            return False, "Advance amount does not match the booking."

    elif payment.purpose == Payment.Purpose.FINAL:
        if booking.status != Booking.Status.COMPLETED:
            return False, "Booking must be completed before final payment."
        if booking.final_payment_method != Booking.FinalPaymentMethod.ONLINE:
            return False, "This booking is not configured for online final payment."

        remaining = total - paid
        if remaining <= 0:
            return False, "No remaining amount is due."
        if amount != remaining:
            return False, "Final payment amount does not match the remaining balance."

    else:
        return False, "Invalid payment purpose."

    if paid + amount > total:
        return False, "Payment would exceed the booking total."

    # Both writes are inside the same DB transaction: either both persist or neither.
    payment.status = Payment.Status.SUCCESS
    payment.sslcommerz_val_id = str(val_id)
    payment.save(update_fields=["status", "sslcommerz_val_id", "updated_at"])

    booking.paid_amount = paid + amount
    if booking.paid_amount >= total:
        booking.paid_amount = total
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.is_paid = True
    else:
        booking.payment_status = Booking.PaymentStatus.PARTIALLY_PAID
        booking.is_paid = False

    booking.save(
        update_fields=["paid_amount", "payment_status", "is_paid", "updated_at"]
    )
    return True, "Payment verified successfully."


def create_payment_session(payment, request):
    booking = payment.booking
    profile = getattr(booking.user, "profile", None)

    post_body = {
        "total_amount": str(_as_money(payment.amount)),
        "currency": "BDT",
        "tran_id": str(payment.transaction_id),
        "success_url": request.build_absolute_uri("/api/v1/payments/success/"),
        "fail_url": request.build_absolute_uri("/api/v1/payments/fail/"),
        "cancel_url": request.build_absolute_uri("/api/v1/payments/cancel/"),
        "ipn_url": request.build_absolute_uri("/api/v1/payments/ipn/"),
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

    result = SSLCOMMERZ(settings.SSLCOMMERZ_SETTINGS).createSession(post_body)
    if not isinstance(result, dict) or not result.get("GatewayPageURL"):
        raise ValueError("SSLCommerz did not return GatewayPageURL.")
    return result["GatewayPageURL"]


def _initiate_payment(request, purpose):
    try:
        booking_id = int(request.data.get("booking_id"))
    except (TypeError, ValueError):
        return Response(
            {"error": "A valid booking_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update(), id=booking_id, user=request.user
        )

        total = _as_money(booking.price_at_booking)
        paid = _as_money(booking.paid_amount)

        if total <= 0 or paid < 0 or paid > total:
            return Response(
                {"error": "Booking payment values are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if purpose == Payment.Purpose.ADVANCE:
            if booking.status != Booking.Status.ACCEPTED:
                return Response(
                    {"error": "Provider must accept the booking first."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if paid > 0:
                return Response(
                    {"error": "An advance payment has already been recorded."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            amount = _as_money(booking.advance_amount)
            if amount <= 0 or amount > total:
                return Response(
                    {"error": "The booking advance amount is invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
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

            amount = total - paid
            if amount <= 0:
                return Response(
                    {"error": "No remaining amount is due."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        pending_exists = Payment.objects.filter(
            booking=booking,
            purpose=purpose,
            status=Payment.Status.PENDING,
        ).exists()
        if pending_exists:
            return Response(
                {"error": "A payment attempt is already pending."},
                status=status.HTTP_409_CONFLICT,
            )

        payment = Payment.objects.create(
            booking=booking,
            purpose=purpose,
            amount=amount,
        )

    try:
        gateway_url = create_payment_session(payment, request)
    except Exception:
        Payment.objects.filter(
            pk=payment.pk, status=Payment.Status.PENDING
        ).update(status=Payment.Status.FAILED)
        return Response(
            {"error": "Could not initiate SSLCommerz payment."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            "payment_id": payment.id,
            "transaction_id": str(payment.transaction_id),
            "purpose": payment.purpose,
            "amount": str(payment.amount),
            "gateway_url": gateway_url,
            "booking_total": str(_as_money(booking.price_at_booking)),
            "booking_advance_amount": str(_as_money(booking.advance_amount)),
            "booking_paid_amount": str(_as_money(booking.paid_amount)),
            "booking_remaining_amount": str(booking.remaining_amount),
        },
        status=status.HTTP_201_CREATED,
    )

@swagger_auto_schema(
    method="post",
    operation_summary="Initiate Advance Payment",
    operation_description=(
        "Customer can pay 20% advance after "
        "the service provider accepts the booking."
    ),
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
        201: openapi.Response(
            description="Payment initiated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER
                    ),
                    "amount": openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                    "gateway_url": openapi.Schema(
                        type=openapi.TYPE_STRING
                    ),
                },
            ),
        ),
        400: "Invalid booking",
        409: "Payment already pending",
        502: "SSLCommerz unavailable",
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsCustomer])
def initiate_advance_payment(request):
    return _initiate_payment(request, Payment.Purpose.ADVANCE)



@swagger_auto_schema(
    method="post",
    operation_summary="Initiate Final Payment",
    operation_description=(
        "Customer pays the remaining amount "
        "after service completion."
    ),
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
        201: "Final payment initiated successfully",
        400: "Invalid booking or no remaining amount",
        409: "Payment already pending",
        502: "SSLCommerz unavailable",
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsCustomer])
def initiate_final_payment(request):
    return _initiate_payment(request, Payment.Purpose.FINAL)

@swagger_auto_schema(
    method="post",
    operation_summary="SSLCommerz Payment Success",
    operation_description=(
        "Validates the transaction with SSLCommerz "
        "and updates the booking payment."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id", "val_id"],
        properties={
            "tran_id": openapi.Schema(
                type=openapi.TYPE_STRING,
            ),
            "val_id": openapi.Schema(
                type=openapi.TYPE_STRING,
            ),
        },
    ),
    responses={
        200: "Payment verified successfully",
        400: "Transaction validation failed",
        502: "Payment verification unavailable",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_success(request):
    tran_id = request.data.get("tran_id")
    val_id = request.data.get("val_id")
    print("CALLBACK DATA:", request.data)
    print("TRAN ID:", request.data.get("tran_id"))
    print("VAL ID:", request.data.get("val_id"))
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
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    # Return updated booking payment info so the frontend can see the changes.
    payment = Payment.objects.select_related("booking").filter(
        transaction_id=tran_id
    ).first()
    if payment:
        booking = payment.booking
        return Response(
            {
                "message": message,
                "payment_id": payment.id,
                "transaction_id": str(payment.transaction_id),
                "purpose": payment.purpose,
                "payment_amount": str(payment.amount),
                "payment_status": payment.status,
                "booking_id": booking.id,
                "booking_paid_amount": str(booking.paid_amount),
                "booking_remaining_amount": str(booking.remaining_amount),
                "booking_payment_status": booking.payment_status,
                "booking_is_paid": booking.is_paid,
            },
            status=status.HTTP_200_OK,
        )
    return Response({"message": message}, status=status.HTTP_200_OK)


def _valid_ipn_signature(payload):
    """Verify SSLCommerz IPN signature using verify_key/verify_sign."""
    verify_key = payload.get("verify_key")
    verify_sign = payload.get("verify_sign")
    store_id = str(settings.SSLCOMMERZ_SETTINGS.get("store_id", ""))
    store_pass = str(settings.SSLCOMMERZ_SETTINGS.get("store_pass", ""))

    if not verify_key or not verify_sign or not store_id or not store_pass:
        return False
    if str(payload.get("store_id", "")) != store_id:
        return False

    signed_values = {}
    for key in str(verify_key).split(","):
        if key in payload:
            signed_values[key] = str(payload[key])

    signed_values["store_passwd"] = hashlib.md5(
        store_pass.encode("utf-8")
    ).hexdigest()
    serialized = "&".join(
        f"{key}={value}" for key, value in sorted(signed_values.items())
    )
    expected_sign = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected_sign, str(verify_sign))

@swagger_auto_schema(
    method="post",
    operation_summary="SSLCommerz IPN",
    operation_description=(
        "Processes SSLCommerz Instant Payment Notification."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id", "val_id"],
        properties={
            "tran_id": openapi.Schema(
                type=openapi.TYPE_STRING,
            ),
            "val_id": openapi.Schema(
                type=openapi.TYPE_STRING,
            ),
        },
    ),
    responses={
        200: "IPN processed successfully",
        400: "Invalid transaction",
        502: "Verification failed",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_ipn(request):
    payload = request.data
    if not _valid_ipn_signature(payload):
        return Response(
            {"error": "Invalid SSLCommerz IPN signature."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    tran_id = payload.get("tran_id")
    gateway_status = str(payload.get("status", "")).upper()
    if not tran_id:
        return Response(
            {"error": "Missing transaction ID."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if gateway_status in {"VALID", "VALIDATED"}:
        val_id = payload.get("val_id")
        if not val_id:
            return Response(
                {"error": "Missing validation ID."},
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
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": message}, status=status.HTTP_200_OK)

    if gateway_status not in {"FAILED", "CANCELLED", "EXPIRED", "UNATTEMPTED"}:
        return Response(
            {"message": "IPN received; no payment state change was made."},
            status=status.HTTP_200_OK,
        )

    # Only a signed IPN can mark a gateway attempt failed/cancelled.
    try:
        reported_amount = _as_money(payload.get("amount"))
    except (InvalidOperation, TypeError, ValueError):
        return Response(
            {"error": "Invalid IPN amount."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        payment = (
            Payment.objects.select_for_update()
            .filter(transaction_id=tran_id)
            .first()
        )
        if payment is None:
            return Response(
                {"error": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if payment.status == Payment.Status.SUCCESS:
            return Response(
                {"message": "Payment is already successful; state unchanged."},
                status=status.HTTP_200_OK,
            )
        if payment.status == Payment.Status.PENDING:
            if (
                reported_amount != _as_money(payment.amount)
                or str(payload.get("currency", "")).upper() != "BDT"
            ):
                return Response(
                    {"error": "IPN amount/currency does not match payment."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])

    return Response(
        {"message": "Gateway payment attempt marked failed."},
        status=status.HTTP_200_OK,
    )

@swagger_auto_schema(
    method="get",
    operation_summary="Check Payment Status",
    operation_description=(
        "Customer checks payment status and "
        "booking paid and remaining amounts."
    ),
    manual_parameters=[
        openapi.Parameter(
            "payment_id",
            openapi.IN_PATH,
            description="Payment ID",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Payment status retrieved",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment_attempt_status": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "booking_payment_status": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "booking_paid_amount": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "booking_remaining_amount": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "booking_is_paid": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                    ),
                },
            ),
        ),
        404: "Payment not found",
    },
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsCustomer])
def payment_status_detail(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("booking"),
        pk=payment_id,
        booking__user=request.user,
    )
    booking = payment.booking
    return Response(
        {
            "payment_id": payment.id,
            "transaction_id": str(payment.transaction_id),
            "purpose": payment.purpose,
            "payment_attempt_status": payment.status,
            "payment_amount": str(payment.amount),
            "booking_payment_status": booking.payment_status,
            "booking_paid_amount": str(booking.paid_amount),
            "booking_remaining_amount": str(booking.remaining_amount),
            "booking_is_paid": booking.is_paid,
        },
        status=status.HTTP_200_OK,
    )

@swagger_auto_schema(
    method="post",
    operation_summary="Confirm Cash Payment",
    operation_description=(
        "Service provider confirms cash collection "
        "after service completion."
    ),
    manual_parameters=[
        openapi.Parameter(
            "booking_id",
            openapi.IN_PATH,
            description="Booking ID",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Cash payment confirmed",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "paid_amount": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "remaining_amount": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                },
            ),
        ),
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

        remaining = _as_money(booking.remaining_amount)
        if remaining <= 0:
            return Response(
                {"error": "Booking is already fully paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.paid_amount = _as_money(booking.paid_amount) + remaining
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.is_paid = True
        booking.save(
            update_fields=["paid_amount", "payment_status", "is_paid", "updated_at"]
        )

    return Response(
        {
            "message": "Cash payment confirmed.",
            "paid_amount": str(booking.paid_amount),
            "remaining_amount": str(booking.remaining_amount),
            "payment_status": booking.payment_status,
            "is_paid": booking.is_paid,
        },
        status=status.HTTP_200_OK,
    )

@swagger_auto_schema(
    method="post",
    operation_summary="Payment Failed or Cancelled",
    operation_description=(
        "Processes failed or cancelled payment attempts."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["tran_id"],
        properties={
            "tran_id": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="SSLCommerz transaction ID",
            ),
        },
    ),
    responses={
        200: openapi.Response(
            description="Payment status processed",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    "updated": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                    ),
                },
            ),
        ),
        400: "Missing transaction ID",
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def payment_failed(request):
    # Do not mark a payment FAILED using an unauthenticated callback containing
    # only a client-visible transaction ID. Verify the gateway status first.
    return Response(
        {
            "message": (
                "Failure/cancellation received. Payment remains pending until "
                "its gateway status is verified."
            ),
            "transaction_id": request.data.get("tran_id"),
        },
        status=status.HTTP_200_OK,
    )
