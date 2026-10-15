from rest_framework import serializers
from .models import Category


def validate_category_name(value, instance=None):
    categories = Category.objects.filter(name__iexact=value)
    if instance is not None:
        categories = categories.exclude(pk=instance.pk)
    if categories.exists():
        raise serializers.ValidationError("Category already exists.")
    return value


class CreateCategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["user", "create_at"]

    def validate_name(self, value):
        return validate_category_name(value)


class CreatedCategoryResponseSerializer(serializers.Serializer):
    category = CreateCategorySerializers()


class CategorySearchResponseSerializer(serializers.Serializer):
    category = CreateCategorySerializers(many=True)


class CategoryUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["user", "create_at"]

    def validate_name(self, value):
        return validate_category_name(value, self.instance)