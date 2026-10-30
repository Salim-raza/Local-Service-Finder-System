from django.db import models
from booking.models import Booking
import uuid

# Create your models here.
class Payment(models.Model):    
    class Purpose(models.TextChoices):
        ADVANCE = "advance", "Advance Payment"
        FINAL = "final", "Final Payment"
        
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="payment")
    transaction_id = models.CharField(default=uuid.uuid4, unique=True, editable=False)
    purpose = models.CharField(max_length=10, choices=Purpose.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    sslcommerz_val_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"