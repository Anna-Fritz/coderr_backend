from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from user_auth_app.models import CustomUser
from profiles_app.models import UserProfile
from rest_framework.authtoken.models import Token


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

