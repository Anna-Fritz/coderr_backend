import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as DRFValidationError

from ..models import UserProfile
from ..api.serializers import BusinessProfileSerializer


class BusinessProfileSerializerTests(TestCase):
    """Test suite for validating the BusinessProfileSerializer functionality."""

    def test_invalid_file_extension(self):
        """Ensure serializer raises an error when an invalid file extension is provided."""
        invalid_file = SimpleUploadedFile("test_image.txt", b"file_content", content_type="text/plain")
        user = get_user_model().objects.create_user(username="testuser2", password="testpassword", type="business")
        profile_data = {
            'user': user.id,
            'file': invalid_file,
            'type': user.type
        }
        serializer = BusinessProfileSerializer(data=profile_data)
        with self.assertRaises(DRFValidationError):
            serializer.is_valid(raise_exception=True)

    def test_file_field_representation(self):
        """Ensure file field returns the correct URL format in serialized data."""
        file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        user = get_user_model().objects.create_user(username="testuser3", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, file=file, type=user.type)
        serializer = BusinessProfileSerializer(profile)
        expected_representation = {
            'user': user.id,
            'username': user.username,
            'file': f"/media/{profile.file.name}",
        }
        self.assertEqual(serializer.data['file'], expected_representation['file'])
        os.remove(profile.file.path)

    def test_update_user_profile(self):
        """Ensure serializer correctly updates an existing user profile."""
        user = get_user_model().objects.create_user(username="testuser", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, first_name="OldFirstName", last_name="OldLastName", type=user.type)
        update_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
        }
        serializer = BusinessProfileSerializer(instance=profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.first_name, 'NewFirstName')
        self.assertEqual(updated_profile.last_name, 'NewLastName')

    def test_create_user_profile(self):
        """Ensure serializer correctly creates a new user profile."""
        user = get_user_model().objects.create_user(username="testuser4", password="testpassword", type="business")
        profile_data = {
            'user': user.id,
            'first_name': 'TestFirstName',
            'last_name': 'TestLastName',
            'type': user.type
        }
        serializer = BusinessProfileSerializer(data=profile_data)
        self.assertTrue(serializer.is_valid())
        created_profile = serializer.save()
        self.assertEqual(created_profile.first_name, 'TestFirstName')
        self.assertEqual(created_profile.last_name, 'TestLastName')

    def test_file_upload_validation_via_serializer(self):
        """Test that serializer raises validation error for oversized file"""
        large_file = SimpleUploadedFile("large.jpg", b"x" * 10**7, content_type="image/jpeg")
        user = get_user_model().objects.create(username="testuser3", password="password", type="business")
        data = {
            "user": user.id,
            "file": large_file,
            "type": user.type,
        }
        serializer = BusinessProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("file", serializer.errors)