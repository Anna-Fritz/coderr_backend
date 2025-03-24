from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


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
