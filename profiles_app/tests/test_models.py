import tempfile
import os
from django.conf import settings
from django.test import TestCase
from ..models import UserProfile
from user_auth_app.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.core.exceptions import ValidationError


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

    def test_profile_file_name_on_save(self):
        """Ensure uploaded files are saved with the correct naming convention."""
        second_user = CustomUser.objects.create_user(username="testuser3", password="testpassword", type="business")
        second_profile = UserProfile.objects.create(user=second_user, file=self.file, type=second_user.type)
        expected_filename = f"profile-imgs/profile_{second_user.id}_{second_user.username}.jpg"
        self.assertEqual(second_profile.file.name, expected_filename)

    def test_uploaded_at_on_save(self):
        """Ensure the uploaded_at field is automatically populated upon file upload."""
        self.assertIsNotNone(self.profile.uploaded_at)
        self.assertTrue(self.profile.uploaded_at <= timezone.now())

    def test_uploaded_at_when_no_file(self):
        """Ensure uploaded_at remains None when no file is uploaded."""
        user = CustomUser.objects.create_user(username="testuser3", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type=user.type)
        self.assertIsNone(profile.uploaded_at)

    def test_invalid_file_extension(self):
        """Ensure an error is raised when an invalid file type is uploaded."""
        invalid_file = SimpleUploadedFile("test_image.txt", b"file_content", content_type="text/plain")
        user = CustomUser.objects.create_user(username="testuser4", password="testpassword", type="business")
        profile = UserProfile.objects.create(user=user, type=user.type, file=invalid_file)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_str_method(self):
        """Ensure the string representation of UserProfile is formatted correctly."""
        expected_str = f"{self.profile.username}, {self.profile.first_name} {self.profile.last_name} ({self.profile.type})"
        self.assertEqual(str(self.profile), expected_str)

    def tearDown(self):
        """Clean up the temporary media directory after each test."""
        import shutil
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)
