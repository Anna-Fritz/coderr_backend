from django.db import models
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size
from django.utils import timezone
from user_auth_app.models import CustomUser
import os
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete

# Create your models here.


class UserProfile(models.Model):
    """
    Extends the CustomUser model with additional profile details.
    """
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
        """
        Saves the UserProfile instance. Auto-fills missing fields (first name, last name, email, and username) 
        from the associated user if not already provided. Handles file replacement by deleting the old file 
        and renaming the new file, if necessary. Updates the uploaded_at timestamp when the file is updated.
        """
        if self.user:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
            if not self.email:
                self.email = self.user.email
            if not self.username:
                self.username = self.user.username

            changed = False
            if self.first_name != self.user.first_name:
                self.user.first_name = self.first_name
                changed = True
            if self.last_name != self.user.last_name:
                self.user.last_name = self.last_name
                changed = True
            if self.email != self.user.email:
                self.user.email = self.email
                changed = True
            if changed:
                self.user.save()

        if self.id:
            original = UserProfile.objects.get(pk=self.id)
            if original.file.name != self.file.name:  # Check if the file has been changed
                # If the file is changed, delete the old file
                if original.file:
                    old_file_path = original.file.path
                    if os.path.exists(old_file_path):
                        default_storage.delete(old_file_path)
                    self.update_file()
            if self.file and self.uploaded_at is None:
                self.update_file()
        super(UserProfile, self).save(*args, **kwargs)

    def update_file(self):
        """
        Renames the uploaded file to a consistent format using the user's ID and username, 
        and updates the uploaded_at timestamp to the current time.
        """
        ext = self.file.name.split('.')[-1]
        new_filename = f"profile_{self.user.id}_{self.user.username}.{ext}"
        self.file.name = new_filename
        self.uploaded_at = timezone.now()

    def delete(self, *args, **kwargs):
        if self.file:
            file_path = self.file.path
            if os.path.exists(file_path):
                default_storage.delete(file_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.username}, {self.first_name} {self.last_name} ({self.type})"


@receiver(post_delete, sender=UserProfile)
def delete_profile_file(sender, instance, **kwargs):
    """
    Deletes the associated file from storage when a UserProfile instance is deleted.
    """
    if instance.file:
        file_path = instance.file.path
        if os.path.exists(file_path):
            default_storage.delete(file_path)

