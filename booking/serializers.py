from rest_framework import serializers
from .models import *


class BookingSerializers(serializers.ModelSerializer):
    remaining_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = [
            "completed_time",
            "price_at_booking",
            "advance_amount",
            "paid_amount",
            "payment_status",
            "status",
            "user",
            "is_paid",
            "cancellation_reason",
            "cancelled_by",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]
        swagger_schema_fields = {
            "example": {
                "booking_date": "2026-10-15",
                "booking_time": "14:30",
            }
        }


class BookingUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["note", "booking_time", "booking_date"]

