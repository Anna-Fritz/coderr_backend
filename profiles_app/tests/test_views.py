from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user_auth_app.models import CustomUser
from profiles_app.models import UserProfile
from rest_framework.authtoken.models import Token
from ..api.views import BusinessProfileListView, CustomerProfileListView
from ..api.serializers import BusinessProfileSerializer, CustomerProfileSerializer


class ProfileDetailTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpassword",
            type="business"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            type=self.user.type
        )
        self.other_user = CustomUser.objects.create_user(
            username="testuser2",
            password="testpassword",
            type="customer"
        )
        self.other_profile = UserProfile.objects.create(
            user=self.other_user,
            type=self.other_user.type
        )
        self.url = reverse('profile-detail', kwargs={'pk': self.user.id})

    def test_get_profile_without_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_with_login(self):
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_existing_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("api/profile/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_retrieve_other_user_profile(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_owner_patch_profile(self):
        self.client.force_authenticate(user=self.user)
        update_data = {"first_name": "TestFirstName"}

        response = self.client.patch(self.url, update_data, format="json")
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.first_name, "TestFirstName")

    def test_other_user_patch_profile(self):
        self.client.force_authenticate(user=self.other_user)
        update_data = {"first_name": "HackedName"}

        response = self.client.patch(self.url, update_data, format="json")
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(self.profile.first_name, "HackedName")

    def test_unauthenticated_user_patch_profile(self):
        update_data = {"first_name": "ForeignUserName"}

        response = self.client.patch(self.url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(self.profile.first_name, "ForeignUserName")

    def test_user_cannot_delete_own_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_other_profile(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_delete_user_profile(self):
        admin_user = CustomUser.objects.create_superuser(username='adminuser', password='adminpassword')
        self.client.force_authenticate(user=admin_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TypeProfileListTests(APITestCase):
    def setUp(self):
        self.business_user = CustomUser.objects.create_user(
            username="testBusinessUser",
            password="testpassword",
            type="business"
        )
        self.business_profile = UserProfile.objects.create(
            user=self.business_user,
            type=self.business_user.type
        )
        self.customer_user = CustomUser.objects.create_user(
            username="testCustomerUser",
            password="testpassword",
            type="customer"
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer_user,
            type=self.customer_user.type
        )

        self.business_url = reverse('business-profile-list')
        self.customer_url = reverse('customer-profile-list')

    def test_get_profile_lists_authenticated(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_lists_unauthenticated(self):
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_business_profiles(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "business")

        for profile in response.data:
            self.assertNotEqual(profile["type"], "customer")

    def test_get_customer_profiles(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "customer")

        for profile in response.data:
            self.assertNotEqual(profile["type"], "business")

    def test_business_profile_list_uses_correct_serializer(self):
        view = BusinessProfileListView()
        self.assertEqual(view.serializer_class, BusinessProfileSerializer)

    def test_customer_profile_list_uses_correct_serializer(self):
        view = CustomerProfileListView()
        self.assertEqual(view.serializer_class, CustomerProfileSerializer)


class EmptyProfileListTests(APIClient):
    def test_get_empty_profile_lists(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.business_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        response = self.client.get(self.customer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

