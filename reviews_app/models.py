from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from user_auth_app.models import CustomUser

# Create your models here.


class Review(models.Model):
    class Meta:
        unique_together = ('business_user', 'reviewer') 

    business_user = models.ForeignKey(CustomUser, related_name="business_reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, related_name="customer_reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username} - {self.rating}★"
