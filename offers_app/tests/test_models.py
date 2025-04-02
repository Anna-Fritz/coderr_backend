import os
import tempfile
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from offers_app.models import Offer, CustomUser


class OfferModelTests(TestCase):
    def setUp(self):
        """Creates a test user for the test cases."""
        self.test_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_root

        self.user = CustomUser.objects.create(username="testuser", email="test@example.com")

    def test_offer_creation(self):
        """Tests if an `Offer` object can be successfully created."""
        offer = Offer.objects.create(title="Test Offer", description="Test Description", user=self.user)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(offer.title, "Test Offer")

    def test_str_method(self):
        """Tests the `__str__()` method of the `Offer` model."""
        offer = Offer.objects.create(title="Test Offer", description="Test Description", user=self.user)
        self.assertEqual(str(offer), f"{offer.title}, {offer.created_at} ({self.user.first_name})")

    def test_image_upload_and_rename(self):
        """Tests if an uploaded image is correctly stored and renamed."""
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        offer.image = image
        offer.save()
        expected_filename = f"offer-imgs/user_{self.user.id}_{self.user.username}_offer_{offer.id}.jpg"
        self.assertEqual(offer.image.name, expected_filename)

    def test_old_image_deleted_on_update(self):
        """Tests if the old image is deleted when a new image is uploaded."""
        old_image = SimpleUploadedFile("old.jpg", b"old_content", content_type="image/jpeg")
        new_image = SimpleUploadedFile("new.jpg", b"new_content", content_type="image/jpeg")

        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        offer.image = old_image
        offer.save()
        old_image_path = offer.image.path
        offer.image = new_image
        offer.save()
        offer.delete()
        self.assertFalse(os.path.exists(old_image_path))  # The old image should be deleted

    def test_image_deleted_on_offer_delete(self):
        """Tests if the associated image is deleted when the `Offer` object is removed."""
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        offer = Offer.objects.create(title="Test", description="Test", user=self.user, image=image)
        image_path = offer.image.path
        offer.delete()
        self.assertFalse(os.path.exists(image_path))  # The image should be deleted

    def test_updated_at_changes_on_update(self):
        """Tests if `updated_at` is updated when an `Offer` object is modified."""
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        old_updated_at = offer.updated_at
        offer.title = "Updated Title"
        offer.save()
        self.assertNotEqual(old_updated_at, offer.updated_at)

    def test_created_at_does_not_change_on_update(self):
        """Tests if `created_at` remains unchanged when an `Offer` object is updated."""
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        old_created_at = offer.created_at
        offer.title = "Updated Title"
        offer.save()
        self.assertEqual(old_created_at, offer.created_at)

    def tearDown(self):
        """Clean up the temporary media directory after each test."""
        import shutil
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)

