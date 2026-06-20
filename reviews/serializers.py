from rest_framework import serializers
from .models import ReviewAndRating


class ReviewAndRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewAndRating
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]