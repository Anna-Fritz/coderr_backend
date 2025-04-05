from django.db import models
from django.core.validators import MinValueValidator

from user_auth_app.models import CustomUser
from profiles_app.models import UserProfile

# Create your models here.


class OrderStatus(models.TextChoices):
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class Order(models.Model):
    customer_user = models.ForeignKey(CustomUser, related_name="customer_orders", on_delete=models.SET_NULL, null=True)
    business_user = models.ForeignKey(CustomUser, related_name="business_orders", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=30)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=25, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.IN_PROGRESS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        valid_types = dict(self._meta.get_field("offer_type").choices)
        if self.offer_type not in valid_types:
            raise ValueError(f"Invalid offer_type: {self.offer_type}")
        
        valid_status_types = dict(self._meta.get_field("status").choices)
        if self.status not in valid_status_types:
            raise ValueError(f"Invalid status: {self.status}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_user.username}, order({self.id})"
