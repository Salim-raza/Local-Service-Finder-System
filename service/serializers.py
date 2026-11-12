from rest_framework import serializers
from .models import *


class ServiceCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = ["provider", "create_at", "update_at"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data["image"] = instance.image.url

        return data
        
class ServiceUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "description", "hour_base_price", "image"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data["image"] = instance.image.url

        return data
            