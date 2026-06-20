from django.db import models
from django.conf import settings
# Create your models here.

class Profile(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'male'),
        ('FEMALE', 'female'),
        ('OTHER', 'other')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_image", null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES , null=True, blank=True)
    city = models.CharField(max_length=400, null=True, blank=True)
    area = models.CharField(max_length=400, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    experience = models.IntegerField(default=0, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.id}"
    





    
    

