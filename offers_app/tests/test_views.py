from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from ..models import Offer, OfferDetail
from user_auth_app.models import CustomUser


class OfferViewSetListActionTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        self.offer = Offer.objects.create(title="Test offer", description="List Test", user=self.user)
        OfferDetail.objects.create(offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=3, price=50, features=[], offer_type="basic")
        OfferDetail.objects.create(offer=self.offer, title="Standard", revisions=2, delivery_time_in_days=2, price=100, features=[], offer_type="standard")
        self.url = reverse('offer-list')
        self.client.force_authenticate(user=self.user)

    def test_offer_list_unauthenticated_user(self):
        """Test that an authenticated user can view the list of offers."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_list_filter(self):
        """Test that filtering by price works."""
        response = self.client.get(self.url, {'min_price': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url, {'max_delivery_time': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_list_search(self):
        """Test that searching by title or description works."""
        response = self.client.get(self.url, {'search': 'Test offer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url, {'search': 'Testing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_list_ordering(self):
        """Test that offers can be ordered by updated_at and min_price."""
        response = self.client.get(self.url, {'ordering': 'updated_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.url, {'ordering': 'min_price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_list_pagination(self):
        """Test that pagination works on the offer list."""
        response = self.client.get('/api/offers/?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfferViewSetCreateActionTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password", type="business")
        self.customer_user = CustomUser.objects.create_user(username="testuser2", password="password", type="customer")
        self.admin_user = CustomUser.objects.create_superuser(username="adminuser", password="password")
        self.data = {
            'title': 'Test Offer',
            'description': 'Test Description',
            'details': [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [
                        "Logo Design",
                        "Visitenkarte"
                    ],
                    "offer_type": "basic"
                },
            ]
        }
        self.url = reverse('offer-list')
        self.client.force_authenticate(user=self.user)

    def test_offer_create_authenticated_business_user(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_user_cannot_create_offer(self):
        self.client.logout()
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_offer(self):
        self.client.logout()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_offer_create_unauthenticated_user(self):
        self.client.logout()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_create_missing_required_fields(self):
        """Test that a 400 error is returned when required fields are missing."""
        data = {'title': 'Test Offer'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_create_invalid_data(self):
        """Test that a 400 error is returned when invalid data is provided."""
        self.client.login(username='testuser', password='password')
        data = {
            'title': 'Test Offer',
            'description': 'Test Description',
            'image': 'invalid_image.pdf',
            'details': [
                {
                    "title": "Basic Design",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [
                        "Logo Design",
                        "Visitenkarte"
                    ],
                    "offer_type": "basic"
                },
            ]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OfferViewSetUpdateActionTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password", type="business")
        self.other_user = CustomUser.objects.create_user(username="second_testuser", password="password", type="business")
        self.offer = Offer.objects.create(title="Test offer", description="List Test", user=self.user)
        self.url = reverse('offer-detail', kwargs={'pk': self.offer.id})

    def test_offer_partial_update_authenticated_user(self):
        """Test that an authenticated user can update an offer."""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Updated Offer Title'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_offer = Offer.objects.get(id=self.offer.id)
        self.assertEqual(updated_offer.title, data['title'])
        self.client.logout()
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_update_authenticated_user_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        data = {'title': 'I am not owner of this offer'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_delete_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_offer_delete_authenticated_user_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_update_delete_admin(self):
        admin_user = CustomUser.objects.create_superuser(username="superuser", password="password")
        self.client.force_authenticate(user=admin_user)
        data = {'title': 'admin test'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class OfferDetailDetailViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password", type="business")
        self.admin_user = CustomUser.objects.create_superuser(username="admin_user", password="password")
        self.offer = Offer.objects.create(title="Test offer", description="List Test", user=self.user)
        self.offerdetail = OfferDetail.objects.create(offer=self.offer, title="Basic", revisions=1, delivery_time_in_days=3, price=50, features=[], offer_type="basic")
        self.url = reverse('offerdetails-detail', kwargs={'pk': self.offerdetail.id})
        self.client.force_authenticate(user=self.user)

    def test_offer_detail_valid_id(self):
        """Test that an offer can be retrieved by a valid ID."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_offer_detail_invalid_id(self):
        """Test that a 404 error is returned for a non-existent offer ID."""
        response = self.client.get('/api/offerdetails/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_offer_as_unauthenticated_user(self):
        """Test for retrieving a single offer as an unauthenticated user"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_offer_as_admin_user(self):
        """Test for retrieving a single offer as an admin user"""
        self.client.logout()
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)