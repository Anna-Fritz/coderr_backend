from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

# from django.core.exceptions import ValidationError
# from ..models import Order, CustomUser, OrderStatus
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

    # def test_review_rating_out_of_range_should_fail(self):
    #     review = Review(
    #         business_user=self.business_user,
    #         reviewer=self.customer_user,
    #         rating=6,
    #         description="Too great review"
    #     )
    #     with self.assertRaises(ValidationError) as context:
    #         review.full_clean()
    #     print(f"exception message {context.exception.message.dict}")
    #     self.assertIn('rating', context.exception.message_dict)
    #     self.assertIn('Ensure this value is less than or equal to 5.', context.exception.message_dict['rating'])

    # def test_review_description_too_long_should_fail(self):
    #     long_text = "a" * 1001
    #     review = Review.objects.create(
    #         business_user=self.business_user,
    #         reviewer=self.customer_user,
    #         rating=4,
    #         description="description"
    #     )
    #     review.description = long_text
    #     review.save()
    #     with self.assertRaises(ValidationError) as context:
    #         review.full_clean()
    #     exception = context.exception  # ✅ hier auf das Exception-Objekt zugreifen
    #     self.assertIn("description", exception.message_dict)
    #     self.assertIn("Ensure this value has at most 1000 characters", exception.message_dict["description"][0])

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
