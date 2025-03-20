from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png']), validate_file_size], blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BusinessProfile(UserProfile):
    location = models.CharField(max_length=30)
    tel = models.CharField(max_length=25)
    description = models.TextField(max_length=250)
    working_hours = models.CharField(max_length=15)
    type = models.CharField(max_length=25, default="business", editable=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.type})"


class CustomerProfile(UserProfile):
    type = models.CharField(max_length=25, default="customer", editable=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.type})"
