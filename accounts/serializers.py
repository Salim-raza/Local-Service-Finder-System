from rest_framework import serializers
from .models import *


class UserCreateSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()
    
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "role", "email", "password", "name", "create_at", "last_login", "is_approved", "is_superuser", "is_active"]
        read_only_fields = ["name", "create_at", "last_login", "is_superuser", "is_approved", "is_active"]
        
    def create(self, validated_data):
        return CustomUser.objects.create_user(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            role=validated_data["role"],
            email=validated_data["email"],
            password=validated_data["password"],
            )
        
    def validate_role(self, value):
        value = value.upper()
        
        if value == "ADMIN":
            raise serializers.ValidationError(
                "You cannot register as admin."
            )
            
        allowed_roles = ["CUSTOMER", "SERVICE_PROVIDER"]

        if value not in allowed_roles:
            raise serializers.ValidationError("Invalid role.")
        return value

class SigninSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
class ChangePasswordSerializers(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
class OtpCreateSerializers(serializers.Serializer):
    email = serializers.EmailField()
    
class RestPasswordSerializers(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()
 