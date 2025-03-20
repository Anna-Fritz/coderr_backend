from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=25)
    file = models.FileField(upload_to='uploads/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png']), validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BusinessUserProfile(UserProfile):
    location = models.CharField(max_length=30)
    tel = models.CharField(max_length=25)
    description = models.TextField(max_length=250)
    working_hours = models.CharField(max_length=15)
    type = models.CharField(max_length=25, default="business", editable=False)
    email = models.EmailField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.type})"


class CustomerUserProfile(UserProfile):
    type = models.CharField(max_length=25, default="customer", editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.type})"

