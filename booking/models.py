from django.db import models
from service.models import Service
from accounts.models import CustomUser  
import uuid

# Create your models here.
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PENDING = "pending", "Payment Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        
    class FinalPaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        ONLINE = "online", "Online Payment"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings")
    note = models.TextField(null=True, blank=True)
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField( max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    final_payment_method = models.CharField(max_length=20, choices=FinalPaymentMethod.choices)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    completed_time = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    cancelled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="cancelled_bookings")
    cancelled_at = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def remaining_amount(self):
        return max(
            self.price_at_booking - self.paid_amount, 0
        )
    
    def __str__(self):
        return f"Booking #{self.id} - {self.user.email}"