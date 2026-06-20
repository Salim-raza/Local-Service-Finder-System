from django.db import models
from django.conf import settings
from service.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class ReviewAndRating(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(null=True, blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.service.name}"