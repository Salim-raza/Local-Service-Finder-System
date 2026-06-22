from django.db import models

# Create your models here.
class Division(models.Model):
    name = models.CharField(max_length=50, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class District(models.Model):
    name = models.CharField(max_length=50, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Upazila(models.Model):
    name = models.CharField(max_length=50, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name