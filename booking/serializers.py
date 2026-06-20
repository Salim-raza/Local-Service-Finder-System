from rest_framework import serializers
from .models import *


class BookingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["book_time", "completed_time", "status", "user"]
        
class BookingUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["note", "booking_data", "booking_"]