from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from ..models import Order


class OrderCountViewTest(APITestCase):
    def setUp(self):
        self.business_user = get_user_model().objects.create_user(username="biz", password="test", type="business")
        self.customer_user = get_user_model().objects.create_user(username="cust", password="test", type="customer")

        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.user,
            title="Test Order",
            revisions=1,
            delivery_time_in_days=10,
            price=500,
            offer_type="basic"
        )
        self.url = reverse('order-count', kwargs={'business_user_id': self.business_user.id})

    def create_order(self, status):
        return Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title="Sample Order",
            status=status
        )

    def test_order_count_view_with_existing_user(self):
        # Create orders (2 in_progress, 1 completed)
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="A", status="in_progress")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="B", status="in_progress")
        Order.objects.create(customer_user=self.customer_user, business_user=self.business_user, title="C", status="completed")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["order_count"], 2)