from django.db import models
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size
from user_auth_app.models import CustomUser
import os
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.utils.timezone import now
from django.core.validators import MinValueValidator


# Create your models here.

class Offer(models.Model):
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='offer-imgs/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_file_size], blank=True, null=True)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.image:
            self.update_image()
        if self.id:
            original = Offer.objects.get(pk=self.id)
            if original.image.name != self.image.name:  # Check if the image has been changed
                # If the image is changed, delete the old image
                if original.image:
                    old_image_path = original.image.path
                    if os.path.exists(old_image_path):
                        default_storage.delete(old_image_path)
                    self.update_image()
            self.updated_at = now()
        super(Offer, self).save(*args, **kwargs)

    def update_image(self):
        """
        Renames the uploaded image to a consistent format using the user's ID and username, 
        and updates the uploaded_at timestamp to the current time.
        """
        ext = self.image.name.split('.')[-1]
        new_image_name = f"user_{self.user.id}_{self.user.username}_offer_{self.id}.{ext}"
        self.image.name = new_image_name

    def delete(self, *args, **kwargs):
        if self.image:
            image_path = self.image.path
            if os.path.exists(image_path):
                default_storage.delete(image_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title}, {self.created_at} ({self.user.first_name})"


@receiver(post_delete, sender=Offer)
def delete_offer_image(sender, instance, **kwargs):
    """
    Deletes the associated image from storage when an Offer instance is deleted.
    """
    if instance.image:
        image_path = instance.image.path
        if os.path.exists(image_path):
            default_storage.delete(image_path)


class OfferDetail(models.Model):
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveSmallIntegerField()
    price = models.IntegerField(validators=[MinValueValidator(0)])
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=25, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])

    def save(self, *args, **kwargs):
        self.full_clean()
        valid_types = dict(self._meta.get_field("offer_type").choices)
        if self.offer_type not in valid_types:
            raise ValueError(f"Invalid offer_type: {self.offer_type}")
        super().save(*args, **kwargs)
