from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Review(models.Model):
    """
    Represents a review left by a customer (reviewer) for a business user.
    """
    class Meta:
        unique_together = ('business_user', 'reviewer')

    business_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="business_reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="customer_reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a readable string representation of the review instance.
        """
        return f"Review by {self.reviewer.username} for {self.business_user.username} - {self.rating}★"
