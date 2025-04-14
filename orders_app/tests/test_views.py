from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order
from offers_app.models import OfferDetail, Offer


class OrderViewSetTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
            type='business'
        )
        self.customer = get_user_model().objects.create_user(
            username="testuser_customer",
            password="testpassword",
            type='customer'
        )
        self.offer = Offer.objects.create(
            title="Offer",
            description="Offer Description",
            user=self.user
        )
        self.offer_detail = OfferDetail.objects.create(
            title="Test Offer",
            revisions=2,
            delivery_time_in_days=5,
            price=200,
            features=["Feature 1"],
            offer_type="basic",
            offer=self.offer
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.user,
            title="Test Order",
            revisions=1,
            delivery_time_in_days=10,
            price=500,
            offer_type="basic"
        )
        self.data = {
            "offer_detail_id": self.offer_detail.id
        }
        self.url = reverse('order-list')
        self.detail_url = reverse('order-detail', kwargs={'pk': self.offer.id})

    def test_unauthenticated_user_cannot_create_order(self):
        """Ensure that unauthenticated users cannot create orders."""

        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        """Test that an authenticated user can create an order."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_user'], self.customer.id)
        self.assertEqual(response.data['business_user'], self.user.id)
        self.assertEqual(response.data['status'], "in_progress")

    def test_only_customer_user_allowed_create_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_offer_detail_id(self):
        """Test that an invalid status value raises a validation error."""
        self.client.force_authenticate(user=self.customer)
        data = {
            "offer_detail_id": 9999    # invalid id
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_update_order_status(self):
        """Test that a user who is not the business user cannot update the order status."""
        self.client.force_authenticate(user=self.customer)  # Non-business user
        data = {
            "status": "completed"  # new status
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status(self):
        """Test that an order's status can be updated."""
        data = {
            "status": "completed"  # new status
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "completed")

    def test_order_detail_not_found(self):
        """Test that a 404 error is returned when the order is not found."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('order-detail', kwargs={'pk': 9999}))  # Non-existing order ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_offer_detail_id_required(self):
        """Test that the offer_detail_id is required."""
        self.client.force_authenticate(user=self.customer)
        data = {
            # offer_detail_id is missing
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offer_detail_id', response.data)

    def test_invalid_data_post(self):
        """Test that an invalid offer_type raises a validation error."""
        self.client.force_authenticate(user=self.customer)
        data = {
            "offer_detail_id": self.offer_detail.id,
            "offer_type": "invalid_type"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_invalid_status(self):
        """Test that an invalid status value cannot be set."""
        self.client.force_authenticate(user=self.user)
        data = {
            "status": "invalid_status"  # Invalid status
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_update_order_unauthorized_field(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New order title"  # unauthorized field
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_orders(self):
        """Test that users can only see their own orders."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_business_user_can_view_order(self):
        """Test that the business user can see the order they are linked to."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_only_admin_delete_orders(self):
        admin = get_user_model().objects.create_superuser(username="admin", password="password", type="business")
        self.client.force_authenticate(user=admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
