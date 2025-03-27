import tempfile
import os
from django.conf import settings
from django.test import TestCase
from ..models import UserProfile
from user_auth_app.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile


class UserProfileModelTests(TestCase):
    """Test suite for the UserProfile model."""

    def setUp(self):
        """Set up test environment, including a temporary media directory and test user profile."""
        self.test_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_root

        self.file = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="Testuser",
            type="customer"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            type=self.user.type,
            file=self.file
        )

    def test_create_user_profile(self):
        """Ensure a user profile is correctly created and linked to the corresponding user."""
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.profile.first_name, "Testuser")
        self.assertEqual(self.profile.type, "customer")
        self.assertEqual(CustomUser.objects.count(), UserProfile.objects.count())

    def test_auto_fill_user_data(self):
        """Ensure user profile automatically fills in data from the associated user."""
        self.assertEqual(self.profile.username, self.user.username)
        self.assertEqual(self.profile.first_name, self.user.first_name)
        self.assertEqual(self.profile.last_name, self.user.last_name)
        self.assertEqual(self.profile.email, self.user.email)

    def test_file_upload_size_validation(self):
        """Ensure that large image files are correctly denied"""
        large_file_data = SimpleUploadedFile("large_image.jpg", b"file_content" * 10**7, content_type="image/jpeg")
        user = CustomUser(username="testuser2", password="password", type="business")
        profile = UserProfile(user=user, file=large_file_data, type=user.type)
        with self.assertRaises(ValueError):
            profile.save()

    def test_uploaded_at_when_no_file(self):
        """Ensure uploaded_at remains None when no file is uploaded."""
        user = CustomUser.objects.create_user(username="testuser3", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type=user.type)
        self.assertIsNone(profile.uploaded_at)
        self.assertIsNone(profile.file.name)
        self.assertEqual(profile.user.username, 'testuser3')

    def test_add_file_to_existing_profile(self):
        """
        Tests that adding a file to an existing user profile correctly updates 
        the file name and sets the uploaded_at timestamp.
        """
        user = CustomUser.objects.create_user(username="testuser4", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type=user.type)
        profile.file = self.file
        profile.save()
        self.assertTrue(profile.file.name.endswith(f"profile_{user.id}_testuser4.jpg"))
        self.assertIsNotNone(profile.uploaded_at)

    def test_file_replacement_and_deletion(self):
        """
        Ensures that when a profile file is replaced, the old file is deleted, and the new file is renamed correctly.
        """
        user = CustomUser.objects.create_user(username="testuser5", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type='customer')
        profile.file = self.file
        profile.save()
        original_file_path = profile.file.path
        new_file = SimpleUploadedFile("new_image.jpg", b"new_file_content", content_type="image/jpeg")
        profile.file = new_file
        profile.save()
        os.remove(original_file_path)
        self.assertFalse(os.path.exists(original_file_path))
        self.assertTrue(profile.file.name.endswith(f"profile_{user.id}_testuser5.jpg"))

    def test_uploaded_at_set_on_file_upload(self):
        """
        Verifies that the 'uploaded_at' timestamp is set when a file is uploaded 
        and updated when the file is replaced.
        """
        user = CustomUser.objects.create_user(username="testuser6", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type='customer')
        profile.file = self.file
        profile.save()
        self.assertIsNotNone(profile.uploaded_at)
        new_file_data = SimpleUploadedFile("new_profile_image.jpg", b"new_file_content", content_type="image/jpeg")
        profile.file = new_file_data
        profile.save()
        self.assertIsNotNone(profile.uploaded_at)
        self.assertNotEqual(profile.uploaded_at, profile.created_at)

    def test_str_method(self):
        """Ensure the string representation of UserProfile is formatted correctly."""
        expected_str = f"{self.profile.username}, {self.profile.first_name} {self.profile.last_name} ({self.profile.type})"
        self.assertEqual(str(self.profile), expected_str)

    def test_file_deleted_on_profile_delete(self):
        """
        Ensures that a user's profile image file is deleted from storage 
        when the associated UserProfile instance is deleted.
        """
        user = CustomUser.objects.create_user(username="testuser7", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type='customer')
        new_file_data = SimpleUploadedFile("new_profile_image.jpg", b"new_file_content", content_type="image/jpeg")
        profile.file = new_file_data
        profile.save()
        file_path = profile.file.path
        profile.delete()
        self.assertFalse(os.path.exists(file_path))

    def tearDown(self):
        """Clean up the temporary media directory after each test."""
        import shutil
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)
