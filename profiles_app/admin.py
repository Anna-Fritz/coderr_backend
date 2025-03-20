from django.contrib import admin
from .models import BusinessProfile, CustomerProfile

# Register your models here.

admin.site.register([BusinessProfile, CustomerProfile])