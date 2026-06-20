from django.db import models
from django.conf import settings


# Create your models here.
class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.id}-{self.name}"