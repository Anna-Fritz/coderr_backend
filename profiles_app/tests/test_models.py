import os
from django.test import TestCase
from ..models import UserProfile
from user_auth_app.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile


class UserProfileModelTests(TestCase):
    """Test suite for the UserProfile model."""

    def setUp(self):

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

    def test_uploaded_at_when_no_file(self):
        """Ensure uploaded_at remains None when no file is uploaded."""
        self.assertIsNone(self.profile.uploaded_at)
        self.assertIsNone(self.profile.file.name)
        self.assertEqual(self.profile.user.username, 'testuser')

    def test_add_file_to_existing_profile(self):
        """
        Tests that adding a file to an existing user profile correctly updates 
        the file name and sets the uploaded_at timestamp.
        """
        self.profile.file = self.file
        self.profile.save()
        self.assertTrue(self.profile.file.name.endswith(f"profile_{self.user.id}_testuser.jpg"))
        self.assertIsNotNone(self.profile.uploaded_at)
        self.user.delete()

    def test_file_replacement_and_deletion(self):
        """
        Ensures that when a profile file is replaced, the old file is deleted, and the new file is renamed correctly.
        """
        self.profile.file = self.file
        self.profile.save()
        original_file_path = self.profile.file.path
        new_file = SimpleUploadedFile("new_image.jpg", b"new_file_content", content_type="image/jpeg")
        self.profile.file = new_file
        self.profile.save()
        os.remove(original_file_path)
        self.assertFalse(os.path.exists(original_file_path))
        self.assertTrue(self.profile.file.name.endswith(f"profile_{self.user.id}_testuser.jpg"))
        self.user.delete()

    def test_uploaded_at_set_on_file_upload(self):
        """
        Verifies that the 'uploaded_at' timestamp is set when a file is uploaded 
        and updated when the file is replaced.
        """
        self.profile.file = self.file
        self.profile.save()
        self.assertIsNotNone(self.profile.uploaded_at)
        new_file_data = SimpleUploadedFile("new_profile_image.jpg", b"new_file_content", content_type="image/jpeg")
        self.profile.file = new_file_data
        self.profile.save()
        self.assertIsNotNone(self.profile.uploaded_at)
        self.assertNotEqual(self.profile.uploaded_at, self.profile.created_at)
        self.user.delete()

    def test_str_method(self):
        """Ensure the string representation of UserProfile is formatted correctly."""
        expected_str = f"{self.profile.username}, {self.profile.first_name} {self.profile.last_name} ({self.profile.type})"
        self.assertEqual(str(self.profile), expected_str)

    def test_file_deleted_on_profile_delete(self):
        """
        Ensures that a user's profile image file is deleted from storage 
        when the associated UserProfile instance is deleted.
        """
        new_file_data = SimpleUploadedFile("new_profile_image.jpg", b"new_file_content", content_type="image/jpeg")
        self.profile.file = new_file_data
        self.profile.save()
        file_path = self.profile.file.path
        self.profile.delete()
        self.assertFalse(os.path.exists(file_path))
        self.user.delete()