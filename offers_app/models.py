from django.db import models
import json
from django.core.validators import FileExtensionValidator
from .api.utils import validate_file_size
from user_auth_app.models import CustomUser


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
        if self.image:
            ext = self.image.name.split('.')[-1]
            new_filename = f"user_{self.user.id}_{self.user.username}_offer_{self.id}.{ext}"
            self.image.name = new_filename
        super(Offer, self).save(*args, **kwargs)


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
