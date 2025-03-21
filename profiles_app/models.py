from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size


# Create your models here.
class CustomUser(AbstractUser):
    type = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('business', 'Business')])

    # Verwende related_name für die Reverse-Beziehungen
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Einzigartiger Name für die Rückbeziehung
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Einzigartiger Name für die Rückbeziehung
        blank=True
    )


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.type})"


class CustomerProfile(UserProfile):

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.type})"
