from rest_framework.test import APITestCase
from reviews_app.models import Review
from ..api.serializers import ReviewSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory


class ReviewSerializerTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = get_user_model().objects.create_user(
            username="customer", password="test", type="customer"
        )
        self.business_user = get_user_model().objects.create_user(
            username="business", password="test", type="business"
        )

    def get_context(self, user):
        request = self.factory.post('/reviews/')
        request.user = user
        return {'request': request}

    def test_valid_review_creation(self):
        data = {
            'business_user': self.business_user.id,
            'rating': 5,
            'description': "Sehr zufrieden"
        }
        serializer = ReviewSerializer(data=data, context=self.get_context(self.customer_user))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        review = serializer.save()
        self.assertEqual(review.reviewer, self.customer_user)
        self.assertEqual(review.business_user, self.business_user)

    def test_duplicate_review_should_fail(self):
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Erste Bewertung"
        )
        data = {
            'business_user': self.business_user.id,
            'rating': 4,
            'description': "Zweite Bewertung"
        }
        serializer = ReviewSerializer(data=data, context=self.get_context(self.customer_user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_valid_review_update(self):
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="OK"
        )
        data = {
            'rating': 4,
            'description': "Besser als gedacht"
        }
        serializer = ReviewSerializer(review, data=data, partial=True, context=self.get_context(self.customer_user))
        self.assertTrue(serializer.is_valid())
        updated_review = serializer.save()
        self.assertEqual(updated_review.rating, 4)

    def test_invalid_review_update_fields_should_fail(self):
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="Ok"
        )
        data = {
            'rating': 2,
            'business_user': self.business_user.id  # ← nicht erlaubt laut update()
        }
        serializer = ReviewSerializer(review, data=data, partial=True, context=self.get_context(self.customer_user))

        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        self.assertIn("Only 'rating' and 'description' can be updated", str(context.exception))

    def test_rating_below_min_should_fail(self):
        data = {
            'business_user': self.business_user.id,
            'rating': 0,
            'description': "Ungültige Bewertung"
        }
        serializer = ReviewSerializer(data=data, context=self.get_context(self.customer_user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)
        self.assertIn('Ensure this value is greater than or equal to 1.', serializer.errors['rating'][0])

    def test_rating_above_max_should_fail(self):
        data = {
            'business_user': self.business_user.id,
            'rating': 6,
            'description': "Ungültige Bewertung"
        }
        serializer = ReviewSerializer(data=data, context=self.get_context(self.customer_user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating', serializer.errors)
        self.assertIn('Ensure this value is less than or equal to 5.', serializer.errors['rating'][0])
