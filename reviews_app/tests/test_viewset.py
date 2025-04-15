from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Review


class ReviewViewSetTest(APITestCase):
    """
    Test suite for the ReviewViewSet API, covering creation, update, read, delete,
    and permission rules for customers, businesses, and admin users.
    """
    def setUp(self):
        """
        Set up common test users and data for use across all test methods.
        """
        self.business_user = get_user_model().objects.create_user(username="business_testuser", password="password", type="business")
        self.other_business_user = get_user_model().objects.create_user(username="other_business_user", password="password", type="business")
        self.customer_user = get_user_model().objects.create_user(username="customer_user", password="password", type="customer")
        self.admin_user = get_user_model().objects.create_superuser(username="admin", password="password", type="business")
        self.review_data = {
            "business_user": self.business_user.id,
            "reviewer": self.customer_user.id,
            "rating": 4,
            "description": "Great!"
        }
        self.url = reverse('review-list')

    def test_authenticated_customer_user_can_create_review(self):
        """
        Ensure a logged-in customer can successfully create a review.
        """
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_authenticated_business_user_cannot_create_review(self):
        """
        Ensure a logged-in business user is forbidden from creating reviews.
        """
        self.client.force_authenticate(user=self.other_business_user)
        response = self.client.post(self.url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_create_review(self):
        """
        Ensure an unauthenticated user cannot create a review.
        """
        response = self.client.post(self.url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reviewer_can_update_review_rating_and_description(self):
        """
        Ensure that a reviewer can update the rating and description of their own review.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="Initial"
        )
        self.client.force_authenticate(user=self.customer_user)
        url = reverse("review-detail", args=[review.id])
        data = {"rating": 4, "description": "Updated text"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)
        self.assertEqual(response.data["description"], "Updated text")

    def test_business_user_cannot_update_review(self):
        """
        Ensure that the business user being reviewed cannot update a review.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="Initial"
        )
        self.client.force_authenticate(user=self.business_user)
        url = reverse("review-detail", args=[review.id])
        data = {"rating": 5, "description": "Updated text"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reviewer_cannot_update_business_user(self):
        """
        Ensure that a reviewer cannot change the associated business user of a review.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description="Nice"
        )
        self.client.force_authenticate(user=self.customer_user)
        url = reverse("review-detail", args=[review.id])
        data = {"business_user": self.other_business_user.id}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only 'rating' and 'description'", str(response.data))

    def test_authenticated_user_can_read_reviews(self):
        """
        Ensure any authenticated user can view existing reviews.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="Neutral"
        )
        self.client.force_authenticate(user=self.other_business_user)  # not reviewer, not business_user
        url = reverse("review-detail", args=[review.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_user_can_read_received_reviews(self):
        """
        Ensure a business user can view reviews written about them.
        """
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=3,
            description="Neutral"
        )
        self.client.force_authenticate(user=self.business_user)
        url = reverse("review-detail", args=[review.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_filter_reviews_by_business_user(self):
        """
        Ensure reviews can be filtered by the business_user query parameter.
        """
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=5, description="1")
        self.client.force_authenticate(user=self.business_user)
        url = reverse("review-list") + f"?business_user_id={self.business_user.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_delete_review(self):
        """
        Ensure an admin user can delete any review.
        """
        self.client.force_authenticate(user=self.admin_user)
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=4, description="x")
        url = reverse("review-detail", args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reviewer_can_delete_own_review(self):
        """
        Ensure a reviewer can delete their own review.
        """
        self.client.force_authenticate(user=self.customer_user)
        review = Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=4, description="x")
        url = reverse("review-detail", args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_customer_cannot_delete_other_review(self):
        """
        Ensure a customer cannot delete someone else's review.
        """
        other_customer = get_user_model().objects.create_user(username="other", password="test", type="customer")
        review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=2,
            description="meh"
        )
        self.client.force_authenticate(user=other_customer)
        url = reverse("review-detail", args=[review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
