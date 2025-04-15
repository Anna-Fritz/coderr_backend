from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model (AbstractUser) 
    with a 'type' field to specify whether the user is a 'customer' or 'business' and a file field for profile image.
    """

    type = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('business', 'Business')])
    file = models.FileField(blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True
    )
