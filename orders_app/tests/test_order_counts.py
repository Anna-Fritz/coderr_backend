from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Order


class OrderCountViewTest(APITestCase):
    """
    Tests for the order count endpoint that returns the number of in-progress orders for a given business user.
    """
    def setUp(self):
        """
        Set up a business user, customer, and sample orders with various statuses.
        """
        self.business_user = get_user_model().objects.create_user(username="biz", password="test", type="business")
        self.customer_user = get_user_model().objects.create_user(username="cust", password="test", type="customer")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="A", revisions="2", delivery_time_in_days="3", price=100.00, offer_type="basic", status="in_progress")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="B", revisions="4", delivery_time_in_days="5", price=200.00, offer_type="standard", status="in_progress")
        self.completed_order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="C", revisions="-1", delivery_time_in_days="7", price=300.00, offer_type="premium", status="in_progress")
        self.url = reverse('order-count', kwargs={'business_user_id': self.business_user.id})
        self.client.force_authenticate(user=self.business_user)

    def test_order_count_view_with_existing_user(self):
        """
        Ensure the order count is correctly returned for an existing business user.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 3)

    def test_order_count_view_with_nonexistent_user(self):
        """
        Ensure a 404 is returned when querying orders for a non-existent business user.
        """
        url = reverse("order-count", kwargs={"business_user_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_order_count_counts_only_in_progress_status(self):
        """
        Ensure the order count only includes orders with status 'in_progress'.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.data["order_count"], 3)
        self.completed_order.status = "completed"
        self.completed_order.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_view_with_non_business_user(self):
        """
        Ensure that querying order count for a customer user returns 404.
        """
        url = reverse("order-count", kwargs={"business_user_id": self.customer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_order_count_view_unauthorized_user(self):
        """
        Ensure unauthenticated users cannot access the order count endpoint.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompletedOrderCountViewTest(APITestCase):
    """
    Tests for the completed order count endpoint for a given business user.
    """
    def setUp(self):
        """
        Set up a business user, customer, and orders with some marked as 'completed'.
        """
        self.business_user = get_user_model().objects.create_user(username="biz", password="test", type="business")
        self.customer_user = get_user_model().objects.create_user(username="cust", password="test", type="customer")
        self.first_order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="A", revisions="2", delivery_time_in_days="3", price=100.00, offer_type="basic", status="in_progress")
        self.second_order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="B", revisions="4", delivery_time_in_days="5", price=200.00, offer_type="standard", status="in_progress")
        self.third_order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="C", revisions="-1", delivery_time_in_days="7", price=300.00, offer_type="premium", status="in_progress")
        self.first_order.status = "completed"
        self.first_order.save()
        self.second_order.status = "completed"
        self.second_order.save()
        self.url = reverse('completed-order-count', kwargs={'business_user_id': self.business_user.id})
        self.client.force_authenticate(user=self.business_user)

    def test_completed_order_count_view_with_existing_user(self):
        """
        Ensure the completed order count is returned correctly for an existing business user.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_completed_order_count_view_with_nonexistent_user(self):
        """
        Ensure a 404 is returned for a non-existent business user when querying completed orders.
        """
        url = reverse("completed-order-count", kwargs={"business_user_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_completed_order_count_counts_only_completed_status(self):
        """
        Ensure only orders with status 'completed' are counted in the completed order count.
        """
        all_orders = Order.objects.filter(business_user=self.business_user).count()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)
        self.assertEqual(all_orders, 3)

    def test_completed_order_count_view_with_non_business_user(self):
        """
        Ensure querying completed order count for a customer user returns 404.
        """
        url = reverse("completed-order-count", kwargs={"business_user_id": self.customer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_completed_order_count_view_unauthorized_user(self):
        """
        Ensure unauthenticated users are not allowed to access the completed order count endpoint.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
