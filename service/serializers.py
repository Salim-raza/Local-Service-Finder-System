from rest_framework import serializers
from .models import *


class ServiceCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ["provider", "create_at", "update_at"]
        
class ServiceUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "description", "our_base_price", "image", "contact_base_price"]
        read_only_fields = ["provider", "create_at", "update_at"]
        
        