from django.db import models
from django.core.validators import MinValueValidator

from user_auth_app.models import CustomUser

# Create your models here.


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Order(models.Model):
    customer_user = models.ForeignKey(CustomUser, related_name="customer_orders", on_delete=models.CASCADE)
    business_user = models.ForeignKey(CustomUser, related_name="business_orders", on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=25, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_user.username}, order({self.id})"
