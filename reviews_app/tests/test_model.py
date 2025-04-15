from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.validators import MaxValueValidator

from reviews_app.models import Review


class ReviewModelTest(TestCase):
    """
    Unit tests for the Review model to verify correct creation, constraints,
    and validations.
    """
    def setUp(self):
        """
        Set up test business and customer users for review creation.
        """
        self.business_user = get_user_model().objects.create_user(username="business_testuser", password="password", type="business")
        self.customer_user = get_user_model().objects.create_user(username="customer_user", password="password", type="customer")

    def test_review_creation_success(self):
        """
        Test successful creation of a review and correct string representation.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Sehr gute Zusammenarbeit!"
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(str(review), f"Review by {self.customer_user.username} for {self.business_user.username} - 4★")

    def test_rating_max_value_validator_applied(self):
        """
        Test that the 'rating' field includes a MaxValueValidator with a limit of 5.
        """
        field = Review._meta.get_field('rating')
        validators = field.validators
        self.assertTrue(any(isinstance(v, MaxValueValidator) and v.limit_value == 5 for v in validators))

    def test_unique_review_per_user_business_should_fail(self):
        """
        Test that a customer cannot create more than one review for the same business user.
        """
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
