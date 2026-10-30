from rest_framework import serializers
from .models import *


class BookingSerializers(serializers.ModelSerializer):
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
        
    def create(self, validated_data):
        service = validated_data["service"]
        if not validated_data.get("price_at_booking"):
            validated_data["price_at_booking"] = service.hour_base_price
        return super().create(validated_data)
        
class BookingUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["note", "booking_time", "booking_date"]
        
