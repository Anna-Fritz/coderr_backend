from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import Order, CustomUser, OrderStatus


class OrderModelTests(TestCase):

    def setUp(self):
        """Set up necessary data for tests"""
        self.customer = CustomUser.objects.create_user(
            username="customer", password="password", type="customer"
        )
        self.business = CustomUser.objects.create_user(
            username="business", password="password", type="business"
        )

    def test_create_order(self):
        """Test creating an order with valid data."""
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Sample Order",
            revisions=1,
            delivery_time_in_days=7,
            price=100,
            offer_type="basic",
            status=OrderStatus.IN_PROGRESS
        )
        self.assertEqual(order.title, "Sample Order")
        self.assertEqual(order.revisions, 1)
        self.assertEqual(order.delivery_time_in_days, 7)
        self.assertEqual(order.price, 100)
        self.assertEqual(order.offer_type, "basic")
        self.assertEqual(order.status, OrderStatus.IN_PROGRESS)
        self.assertEqual(order.customer_user.username, "customer")
        self.assertEqual(order.business_user.username, "business")

    def test_invalid_order_status(self):
        """Test that an invalid order status raises an error."""
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer_user=self.customer,
                business_user=self.business,
                title="Invalid Status Order",
                revisions=1,
                delivery_time_in_days=7,
                price=100,
                offer_type="basic",
                status="invalid_status"    # invalid status
            )

    def test_invalid_offer_type(self):
        """Test that an invalid offer type raises an error."""
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer_user=self.customer,
                business_user=self.business,
                title="Invalid Offer Type Order",
                revisions=1,
                delivery_time_in_days=7,
                price=100,
                offer_type="invalid_offer_type",    # invalid offer type
                status=OrderStatus.IN_PROGRESS
            )

    def test_order_timestamps(self):
        """Test that created_at and updated_at are set correctly."""
        order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Timestamp Test Order",
            revisions=1,
            delivery_time_in_days=7,
            price=100,
            offer_type="basic",
            status=OrderStatus.IN_PROGRESS
        )
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)

    def test_invalid_revisions(self):
        """Test that an invalid revisions value raises a validation error."""
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer_user=self.customer,
                business_user=self.business,
                title="Invalid Revisions Order",
                revisions=-2,    # invalid revisions
                delivery_time_in_days=7,
                price=100,
                offer_type="basic",
                status=OrderStatus.IN_PROGRESS
            )
