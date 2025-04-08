# Generated by Django 5.1.7 on 2025-04-08 22:54

from django.db import migrations
import os
from django.core.files import File
from django.contrib.auth.hashers import make_password


def create_guest_users(apps, schema_editor):
    CustomUser = apps.get_model('user_auth_app', 'CustomUser')
    UserProfile = apps.get_model('profiles_app', 'UserProfile')

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # migrations -> app -> project root

    # === Gast-User 1: Kevin ===
    kevin_img_path = os.path.join(base_dir, 'assets', 'ai_generated_profile_img_kevin.png')
    with open(kevin_img_path, 'rb') as f1:
        kevin_file = File(f1, name='ai_generated_profile_img_kevin.png')

        kevin_user = CustomUser.objects.create(
            username="kevin",
            password=make_password("asdasd24"),
            type="business",
            first_name="Kevin",
            last_name="Kovacs",
            email="kevin@mail.de",
            file=kevin_file
        )

        UserProfile.objects.create(
            user=kevin_user,
            username=kevin_user.username,
            type=kevin_user.type,
            first_name=kevin_user.first_name,
            last_name=kevin_user.last_name,
            email=kevin_user.email,
            description="Hallo! Ich bin Kevin, ein erfahrener Full-Stack Entwickler mit Spezialisierung auf Backend- und Frontend-Technologien. Mit über 5 Jahren Erfahrung in der Webentwicklung biete ich dir individuelle und performante Lösungen, die genau auf deine Bedürfnisse zugeschnitten sind.",
            tel="01659854639",
            location="Hannover, Niedersachsen",
            working_hours="Mo-Mi: 18–19 Uhr",
            file=kevin_file
        )

    # === Gast-User 2: Andrey ===
    andrey_img_path = os.path.join(base_dir, 'assets', 'ai_generated_profile_img_andrey.jpg')
    with open(andrey_img_path, 'rb') as f2:
        andrey_file = File(f2, name='ai_generated_profile_img_andrey.jpg')

        andrey_user = CustomUser.objects.create(
            username="andrey",
            password=make_password("asdasd"),
            type="customer",
            first_name="Andrey",
            last_name="Usuf",
            email="andrey@usw.de",
            file=andrey_file
        )

        UserProfile.objects.create(
            user=andrey_user,
            username=andrey_user.username,
            type=andrey_user.type,
            first_name=andrey_user.first_name,
            last_name=andrey_user.last_name,
            email=andrey_user.email,
            file=andrey_file
        )


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0002_customuser_file'),
    ]

    operations = [
        migrations.RunPython(create_guest_users),
    ]
