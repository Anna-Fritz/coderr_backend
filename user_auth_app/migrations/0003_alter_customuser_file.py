# Generated by Django 5.1.7 on 2025-04-09 10:01

import django.core.validators
import profiles_app.api.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0002_customuser_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), profiles_app.api.utils.validate_file_size]),
        ),
    ]
