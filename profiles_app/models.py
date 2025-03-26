from django.db import models
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size
from django.utils import timezone
from user_auth_app.models import CustomUser


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    file = models.FileField(upload_to='profile-imgs/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_file_size], blank=True, null=True)
    uploaded_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    type = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('business', 'Business')], editable=False, null=False, blank=False)
    location = models.CharField(max_length=30, blank=True, null=True)
    tel = models.CharField(max_length=25, blank=True, null=True)
    description = models.TextField(max_length=250, blank=True, null=True)
    working_hours = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.user:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
            if not self.email:
                self.email = self.user.email
            if not self.username:
                self.username = self.user.username
        if self.file and not self.uploaded_at:
            self.uploaded_at = timezone.now()
        if self.file:
            ext = self.file.name.split('.')[-1]
            new_filename = f"profile_{self.user.id}_{self.user.username}.{ext}"
            self.file.name = new_filename
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}, {self.first_name} {self.last_name} ({self.type})"
