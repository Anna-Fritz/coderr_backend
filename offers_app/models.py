from django.db import models
import json
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size
from user_auth_app.models import CustomUser
import os
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete


# Create your models here.

class Offer(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='profile-imgs/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_file_size], blank=True, null=True)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.IntegerField()
    min_delivery_time = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.id:
            original = Offer.objects.get(pk=self.id)
            if original.image.name != self.image.name:  # Check if the file has been changed
                # If the file is changed, delete the old file
                if original.image:
                    old_file_path = original.image.path
                    if os.path.exists(old_file_path):
                        default_storage.delete(old_file_path)
                    self.update_file()
            if self.image and self.updated_at is None:
                self.update_file()
        super(Offer, self).save(*args, **kwargs)

    def update_file(self):
        """
        Renames the uploaded file to a consistent format using the user's ID and username, 
        and updates the uploaded_at timestamp to the current time.
        """
        ext = self.image.name.split('.')[-1]
        new_filename = f"user_{self.user.id}_{self.user.username}_offer_{self.id}.{ext}"
        self.image.name = new_filename

    def delete(self, *args, **kwargs):
        if self.image:
            file_path = self.image.path
            if os.path.exists(file_path):
                default_storage.delete(file_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, {self.created_at} ({self.user.first_name})"


@receiver(post_delete, sender=Offer)
def delete_profile_file(sender, instance, **kwargs):
    """
    Deletes the associated file from storage when a UserProfile instance is deleted.
    """
    if instance.file:
        file_path = instance.file.path
        if os.path.exists(file_path):
            default_storage.delete(file_path)


class Offerdetails(models.Model):
    title = models.CharField(max_length=30)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.TextField(max_length=1000)
    offer_type = models.CharField(max_length=25, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')], editable=False, null=False, blank=False)
    offer_id = models.ForeignKey(Offer, related_name="details", on_delete=models.CASCADE)

    def set_features(self, value):
        self.features = json.dumps(value)    # converts python-list of strings to json format

    def get_features(self):
        return json.loads(self.features)     # converts json data back to python-list of strings
