from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user", "is_verified", "is_available", "latitude", "longitude"]
        
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["image", "gender", "city", "area", "phone", "bio", "experience"]
        read_only_fields = ["user", "is_verified", "is_available", "latitude", "longitude"]
        

