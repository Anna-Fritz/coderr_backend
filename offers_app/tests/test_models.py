import os
import tempfile

from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from offers_app.models import Offer, OfferDetail


class OfferModelTests(TestCase):
    """
    Test suite for the Offer model, ensuring proper behavior of offer-related functionality.
    """
    def setUp(self):
        """
        Creates a test user for the test cases.
        """
        self.test_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_root

        self.user = get_user_model().objects.create(username="testuser", email="test@example.com")

    def test_offer_creation(self):
        """
        Tests if an `Offer` object can be successfully created.
        """
        offer = Offer.objects.create(title="Test Offer", description="Test Description", user=self.user)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(offer.title, "Test Offer")

    def test_str_method(self):
        """
        Tests the `__str__()` method of the `Offer` model.
        """
        offer = Offer.objects.create(title="Test Offer", description="Test Description", user=self.user)
        self.assertEqual(str(offer), f"Business User: {self.user.first_name} {self.user.last_name}, Offer: {offer.id}")

    def test_image_upload_and_rename(self):
        """
        Tests if an uploaded image is correctly stored and renamed.
        """
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        offer.image = image
        offer.save()
        expected_filename = f"offer-imgs/user_{self.user.id}_{self.user.username}_offer_{offer.id}.jpg"
        self.assertEqual(offer.image.name, expected_filename)
        offer.delete()

    def test_old_image_deleted_on_update(self):
        """
        Tests if the old image is deleted when a new image is uploaded.
        """
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
        """
        Tests if the associated image is deleted when the `Offer` object is removed.
        """
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        offer = Offer.objects.create(title="Test", description="Test", user=self.user, image=image)
        image_path = offer.image.path
        offer.delete()
        self.assertFalse(os.path.exists(image_path))  # The image should be deleted

    def test_updated_at_changes_on_update(self):
        """
        Tests if `updated_at` is updated when an `Offer` object is modified.
        """
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        old_updated_at = offer.updated_at
        offer.title = "Updated Title"
        offer.save()
        self.assertNotEqual(old_updated_at, offer.updated_at)

    def test_created_at_does_not_change_on_update(self):
        """
        Tests if `created_at` remains unchanged when an `Offer` object is updated.
        """
        offer = Offer.objects.create(title="Test", description="Test", user=self.user)
        old_created_at = offer.created_at
        offer.title = "Updated Title"
        offer.save()
        self.assertEqual(old_created_at, offer.created_at)

    def tearDown(self):
        """
        Clean up the temporary media directory after each test.
        """
        import shutil
        if os.path.exists(self.test_media_root):
            shutil.rmtree(self.test_media_root)


class OfferDetailModelTests(TestCase):
    """
    Test suite for the OfferDetail model.
    """

    def setUp(self):
        """
        Create a test user and offer for OfferDetail.
        """
        self.user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.offer = Offer.objects.create(title="Test Offer", description="Test Description", user=self.user)

    def test_create_offer_detail(self):
        """
        Test if an OfferDetail can be created and saved properly.
        """
        offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Fast delivery", "Unlimited revisions"],
            offer_type="basic"
        )
        self.assertEqual(OfferDetail.objects.count(), 1)
        self.assertEqual(offer_detail.offer, self.offer)
        self.assertEqual(offer_detail.title, "Basic Package")
        self.assertEqual(offer_detail.revisions, 2)
        self.assertEqual(offer_detail.delivery_time_in_days, 5)
        self.assertEqual(offer_detail.price, 100)
        self.assertEqual(offer_detail.features, ["Fast delivery", "Unlimited revisions"])
        self.assertEqual(offer_detail.offer_type, "basic")

    def test_invalid_offer_type(self):
        """
        Test that an invalid offer_type raises an error.
        """
        with self.assertRaises(ValidationError):
            OfferDetail.objects.create(
                offer=self.offer,
                title="Invalid Package",
                revisions=1,
                delivery_time_in_days=3,
                price=50,
                features=["Test feature"],
                offer_type="gold"  # Unvalid type
            )

    def test_negative_price_not_allowed(self):
        """
        Ensure negative prices are not allowed.
        """
        with self.assertRaises(ValidationError):
            OfferDetail.objects.create(
                offer=self.offer,
                title="Invalid Price",
                revisions=1,
                delivery_time_in_days=3,
                price=-10,  # Unvalid
                features=["Invalid feature"],
                offer_type="basic"
            )

    def test_negative_revisions_not_allowed(self):
        """
        Ensure that revisions cannot be negative, except of -1 for unlimited revisions.
        """
        with self.assertRaises(ValidationError):
            OfferDetail.objects.create(
                offer=self.offer,
                title="Invalid Price",
                revisions=-2,  # Unvalid
                delivery_time_in_days=3,
                price=50,
                features=["Invalid feature"],
                offer_type="basic"
            )

    def test_delete_offer_cascade(self):
        """
        Ensure OfferDetail entries are deleted when the related Offer is deleted.
        """
        OfferDetail.objects.create(
            offer=self.offer,
            title="Test Package",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Feature A", "Feature B"],
            offer_type="basic"
        )
        self.assertEqual(OfferDetail.objects.count(), 1)
        self.offer.delete()
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_json_field_stores_list(self):
        """
        Ensure JSONField correctly stores and retrieves a list.
        """
        offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="JSON Test",
            revisions=1,
            delivery_time_in_days=2,
            price=99,
            features=["Feature 1", "Feature 2"],
            offer_type="standard"
        )
        self.assertIsInstance(offer_detail.features, list)
        self.assertEqual(offer_detail.features, ["Feature 1", "Feature 2"])

    def test_json_field_default_value(self):
        """
        Ensure JSONField default value is an empty list.
        """
        offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="No Features",
            revisions=1,
            delivery_time_in_days=2,
            price=99,
            offer_type="standard"
        )
        self.assertEqual(offer_detail.features, [])

    def test_offer_detail_relationship(self):
        """
        Ensure OfferDetail entries are correctly linked to an Offer.
        """
        offer = Offer.objects.create(title="Main Offer", description="Main Description", user=self.user)
        detail1 = OfferDetail.objects.create(
            offer=offer, title="Basic", revisions=2, delivery_time_in_days=5, price=50, offer_type="basic"
        )
        detail2 = OfferDetail.objects.create(
            offer=offer, title="Premium", revisions=5, delivery_time_in_days=3, price=150, offer_type="premium"
        )

        self.assertEqual(offer.details.count(), 2)
        self.assertIn(detail1, offer.details.all())
        self.assertIn(detail2, offer.details.all())

