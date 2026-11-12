from rest_framework import serializers
from .models import *


class ServiceCreateSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ["provider", "create_at", "update_at"]
        
class ServiceUpdateSerializers(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    class Meta:
        model = Service
        fields = ["name", "description", "hour_base_price", "image"]
        read_only_fields = ["provider", "create_at", "update_at"]
        
        