from django.db import models
from django.contrib.auth.models import AbstractUser
from locations.models import Division, District, Upazila
from .usermanager import CustomUserManager
from django.utils import timezone
import datetime


# Create your models here.
class CustomUser(AbstractUser):  
    ROLE_CHOICE = (
        ("CUSTOMER", "Customer"),
        ("SERVICE_PROVIDER", "Service Provider"),
        ("ADMIN", "Admin")
    )
    username = None
    name = models.CharField(max_length=150, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=50, choices=ROLE_CHOICE, default="CUSTOMER")
    email = models.EmailField(max_length=250, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    upazila = models.ForeignKey(Upazila, on_delete=models.CASCADE, null=True, blank=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    

    def save(self, *args, **kwargs):
        self.name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.id} - {self.email} - {self.role}" 
        
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    create_at = models.DateTimeField(auto_now_add=True)

    def is_expire(self):   
        return timezone.now() > self.create_at + datetime.timedelta(minutes=5) 


    
