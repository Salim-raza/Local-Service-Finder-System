from django.db import models
from django.conf import settings
from categories.models import Category

# Create your models here.
class Service(models.Model):
    class PricingType(models.TextChoices):
        FIXED = "fixed", "Fixed Price"
        HOURLY = "hourly", "Hourly Price"
        QUOTATION = "quotation", "Custom Quotation"
        
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=200, db_index=True)
    image = models.ImageField(upload_to="service_image", max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
    pricing_type = models.CharField( max_length=20, choices=PricingType.choices, default=PricingType.FIXED)
    hour_base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2,  null=True, blank=True)
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}----{self.id}"
    
    
