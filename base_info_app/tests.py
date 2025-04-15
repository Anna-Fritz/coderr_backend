from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review
from offers_app.models import Offer

# Create your tests here.


class BaseInfoTest(APITestCase):
    def setUp(self):
        self.business_user = get_user_model().objects.create_user(username="biz", password="password", type="busines")
        self.customer_user = get_user_model().objects.create_user(username="customer", password="password", type="customer")
        self.other_customer_user = get_user_model().objects.create_user(username="other_user", password="password", type="customer")
        self.url = reverse('base-info')

    def test_base_info_view_is_public(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_view_with_no_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "review_count": 0,
            "average_rating": "0.0",
            "business_profile_count": 1,
            "offer_count": 0,
        })

    def test_base_info_view_with_data(self):
        Review.objects.create(business_user=self.business_user, reviewer=self.customer_user, rating=3, description="Initial")
        Review.objects.create(business_user=self.business_user, reviewer=self.other_customer_user, rating=4, description="Initial")
        Offer.objects.create(title="Test offer", description="List Test", user=self.business_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["review_count"], 2)
        self.assertEqual(response.data["average_rating"], "3.5")
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["offer_count"], 1)

    def test_base_info_view_response_format(self):
        Review.objects.create(business_user=self.business_user, reviewer=self.other_customer_user, rating=4, description="Initial")
        response = self.client.get(self.url)
        data = response.data
        self.assertIsInstance(data['review_count'], int)
        self.assertIsInstance(data['average_rating'], str)
        self.assertIsInstance(data['business_profile_count'], int)
        self.assertIsInstance(data['offer_count'], int)
