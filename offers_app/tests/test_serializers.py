from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from ..models import Offer, OfferDetail
from offers_app.api.serializers import OfferDetailSerializer, OfferCreateSerializer, OfferUpdateSerializer, OfferListSerializer, OfferDetailViewSerializer


class OfferDetailSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.offer = Offer.objects.create(title="Test Offer", description="Test", user=self.user)

    def test_valid_serializer(self):
        """Test that a valid serializer does not raise errors"""
        data = {
            "title": "Basic Package",
            "revisions": 1,
            "delivery_time_in_days": 3,
            "price": 50,
            "features": ["Feature 1"],
            "offer_type": "basic"
        }
        serializer = OfferDetailSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_offer_type(self):
        """Test that an invalid offer_type raises a validation error"""
        data = {
            "title": "Basic Package",
            "revisions": 1,
            "delivery_time_in_days": 3,
            "price": 50,
            "features": ["Feature 1"],
            "offer_type": "gold"  # invalid type
        }
        serializer = OfferDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("offer_type", serializer.errors)

    def test_negative_price_not_allowed(self):
        """Test that a negative price raises a validation error"""
        data = {
            "title": "Basic Package",
            "revisions": 1,
            "delivery_time_in_days": 3,
            "price": -10,
            "features": ["Feature 1"],
            "offer_type": "basic"
        }
        serializer = OfferDetailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)


class OfferCreateSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.request = self.factory.post("/")  # simulates POST-Request
        self.request.user = self.user  # add user

    def test_create_offer_with_details(self):
        """Test that an offer is created correctly with details"""
        data = {
            "title": "New Offer",
            "description": "This is a test offer",
            "details": [
                {"title": "Basic Package", "revisions": 1, "delivery_time_in_days": 3, "price": 50, "features": [], "offer_type": "basic"}
            ]
        }
        serializer = OfferCreateSerializer(data=data, context={"request": self.request})
        self.assertTrue(serializer.is_valid())
        offer = serializer.save()
        self.assertEqual(offer.details.count(), 1)

    def test_invalid_image_extension(self):
        """Test that an invalid image extension raises a validation error"""
        image = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        data = {"image": image}
        serializer = OfferCreateSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class OfferUpdateSerializerTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.offer = Offer.objects.create(title="Update Test", description="Update Test", user=self.user)
        self.detail = OfferDetail.objects.create(
            offer=self.offer, title="Basic Package", revisions=1, delivery_time_in_days=3, price=50, features=[], offer_type="basic"
        )

    def test_update_offer_details(self):
        """Test updating an existing offer detail"""
        data = {
            "id": self.offer.id,
            "title": "Updated Offer",
            "description": "Updated Description",
            "details": [
                {
                    "id": self.detail.id,
                    "title": "Updated Package",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["New Feature"],
                    "offer_type": "standard"
                }
            ]
        }
        serializer = OfferUpdateSerializer(instance=self.offer, data=data)
        self.assertTrue(serializer.is_valid())
        updated_offer = serializer.save()
        updated_detail = updated_offer.details.get(id=self.detail.id)
        self.assertEqual(updated_detail.title, "Updated Package")
        self.assertEqual(updated_detail.revisions, 2)
        self.assertEqual(updated_detail.price, 100)

    def test_update_non_existing_detail(self):
        """Test that updating a non-existing OfferDetail raises an error"""
        data = {
            "id": self.offer.id,
            "title": "Offer Title",
            "description": "Offer Description",
            "details": [
                {
                    "id": 9999,  # not existing ID
                    "title": "Non-existent Package",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": 50,
                    "features": [],
                    "offer_type": "basic"
                }
            ]
        }
        serializer = OfferUpdateSerializer(instance=self.offer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("details", serializer.errors)


class OfferSerializerGetResponseTest(TestCase):  # Tests OfferListSerializer and OfferDetailViewSerializer - GET Response
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.offer = Offer.objects.create(title="List Test", description="List Test", user=self.user)
        OfferDetail.objects.create(offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=3, price=50, features=[], offer_type="basic")
        OfferDetail.objects.create(offer=self.offer, title="Standard", revisions=2, delivery_time_in_days=2, price=100, features=[], offer_type="standard")
        self.request = self.factory.get("/")  # simulates GET-Request
        self.request.user = self.user  # add user

    def test_min_price_calculation(self):
        """Test that the minimum price is calculated correctly"""
        serializer = OfferListSerializer(instance=self.offer, context={"request": self.request})
        self.assertEqual(serializer.data["min_price"], 50)
        serializer = OfferDetailViewSerializer(instance=self.offer, context={"request": self.request})
        self.assertEqual(serializer.data["min_price"], 50)

    def test_min_delivery_time_calculation(self):
        """Test that the minimum delivery time is calculated correctly"""
        serializer = OfferListSerializer(instance=self.offer, context={"request": self.request})
        self.assertEqual(serializer.data["min_delivery_time"], 2)
        serializer = OfferDetailViewSerializer(instance=self.offer, context={"request": self.request})
        self.assertEqual(serializer.data["min_delivery_time"], 2)

    def test_details_format(self):
        """Test that the details field contains the expected URLs"""
        serializer = OfferListSerializer(instance=self.offer, context={"request": self.request})
        details = serializer.data["details"]
        self.assertEqual(len(details), 2)
        serializer = OfferDetailViewSerializer(instance=self.offer, context={"request": self.request})
        self.assertEqual(len(details), 2)

    def test_user_details_serialization(self):
        """Test that user_details are correctly serialized"""
        serializer = OfferListSerializer(instance=self.offer, context={"request": self.request})
        expected_user_details = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "username": self.user.username
        }
        self.assertEqual(serializer.data["user_details"], expected_user_details)
