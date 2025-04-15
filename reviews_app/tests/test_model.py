from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.validators import MaxValueValidator

from reviews_app.models import Review


class ReviewModelTest(TestCase):
    def setUp(self):
        self.business_user = get_user_model().objects.create_user(username="business_testuser", password="password", type="business")
        self.customer_user = get_user_model().objects.create_user(username="customer_user", password="password", type="customer")

    def test_review_creation_success(self):
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr gute Zusammenarbeit!"
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(str(review), f"Review by {self.customer_user.username} for {self.business_user.username} - 4★")

    def test_rating_max_value_validator_applied(self):
        field = Review._meta.get_field('rating')
        validators = field.validators
        self.assertTrue(any(isinstance(v, MaxValueValidator) and v.limit_value == 5 for v in validators))

    def test_unique_review_per_user_business_should_fail(self):
        Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=5,
            description="Top Service!"
        )
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                business_user=self.business_user,
                reviewer=self.customer_user,
                rating=3,
                description="Oops, reviewed twice!"
            )
