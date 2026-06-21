from rest_framework import serializers
from .models import *


class BookingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["book_time", "completed_time", "status", "user"]
        
    def create(self, validated_data):
        service = validated_data["service"]
        if not validated_data.get("final_price"):
            validated_data["final_price"] = service.our_base_price
        return super().create(validated_data)
        
class BookingUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["note", "booking_data", "booking_"]