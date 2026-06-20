from rest_framework import serializers
from .models import *


class CreateCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["user", "create_at"]
        

class CategoryUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["user", "create_at"]
    
    def validated_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            return serializers.ValidationError("Category Already Exists")
        return value