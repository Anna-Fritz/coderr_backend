import os
from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.validators import MinValueValidator

from .api.utils import validate_file_size


# Create your models here.

class Offer(models.Model):
    """
    Represents an offer created by a business user, including details such as title, image, description, 
    and associated user, with functionality for managing image uploads and deletions.
    """
    title = models.CharField(max_length=50)
    image = models.FileField(upload_to='offer-imgs/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_file_size], blank=True, null=True)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='offers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Saves the offer instance and renames the image if changed, deleting old images if necessary.
        """
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
        """
        Deletes the associated image file from storage when the offer is deleted.
        """
        if self.image:
            image_path = self.image.path
            if os.path.exists(image_path):
                default_storage.delete(image_path)
        super().delete(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the offer including business user and offer ID.
        """
        return f"Business User: {self.user.first_name} {self.user.last_name}, Offer: {self.id}"


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
    """
    Represents detailed specifications for a particular offer, including revisions, price, delivery time, 
    features, and type of offer.
    """
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=25, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')])

    def save(self, *args, **kwargs):
        """
        Validates the offer type and saves the offer detail instance.
        """
        self.full_clean()
        valid_types = dict(self._meta.get_field("offer_type").choices)
        if self.offer_type not in valid_types:
            raise ValueError(f"Invalid offer_type: {self.offer_type}")
        super().save(*args, **kwargs)
