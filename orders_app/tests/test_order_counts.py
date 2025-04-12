from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Order


class OrderCountViewTest(APITestCase):
    def setUp(self):
        self.business_user = get_user_model().objects.create_user(username="biz", password="test", type="business")
        self.customer_user = get_user_model().objects.create_user(username="cust", password="test", type="customer")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="A", revisions="2", delivery_time_in_days="3", price=100.00, offer_type="basic", status="in_progress")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="B", revisions="4", delivery_time_in_days="5", price=200.00, offer_type="standard", status="in_progress")
        self.completed_order = Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="C", revisions="-1", delivery_time_in_days="7", price=300.00, offer_type="premium", status="in_progress")
        self.url = reverse('order-count', kwargs={'business_user_id': self.business_user.id})
        self.client.force_authenticate(user=self.business_user)

    def test_order_count_view_with_existing_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 3)

    def test_order_count_view_with_nonexistent_user(self):
        url = reverse("order-count", kwargs={"business_user_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_order_count_counts_only_in_progress_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["order_count"], 3)
        self.completed_order.status = "completed"
        self.completed_order.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 2)

    def test_order_count_view_with_non_business_user(self):
        url = reverse("order-count", kwargs={"business_user_id": self.customer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_order_count_view_unauthorized_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CompletedOrderCountViewTest(APITestCase):
    def setUp(self):
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_completed_order_count_view_with_nonexistent_user(self):
        url = reverse("completed-order-count", kwargs={"business_user_id": 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_completed_order_count_counts_only_completed_status(self):
        all_orders = Order.objects.filter(business_user=self.business_user).count()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)
        self.assertEqual(all_orders, 3)

    def test_completed_order_count_view_with_non_business_user(self):
        url = reverse("completed-order-count", kwargs={"business_user_id": self.customer_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_completed_order_count_view_unauthorized_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
