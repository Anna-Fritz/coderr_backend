from django.test import TestCase
from rest_framework.test import APIClient
from profiles_app.models import UserProfile
from ..api.serializers import RegistrationSerializer
from ..models import CustomUser
from rest_framework import status


class RegistrationSerializerTests(TestCase):
    """
    Test suite for the RegistrationSerializer to validate user registration functionality.
    """

    def test_successful_registration(self):
        """
        Test case to verify that a user can be successfully registered with valid data 
        and the corresponding profile is created.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "securepassword",
            "type": "customer"
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()
        self.assertEqual(profile.user.username, "newuser")
        self.assertEqual(profile.type, "customer")
        self.assertTrue(profile.user.check_password("securepassword"))

    def test_password_is_write_only(self):
        """
        Test case to check that the password field is write-only in the serializer.
        """
        serializer = RegistrationSerializer()
        self.assertTrue(serializer.Meta.extra_kwargs["password"]["write_only"])

    def test_passwords_must_match(self):
        """
        Test case to ensure that an error is raised when the password and repeated password fields do not match.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "wrongpassword",
            "type": "customer"
        }
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_username_must_be_unique(self):
        """
        Test case to verify that a ValidationError is raised if a username is not unique.
        """
        CustomUser.objects.create_user(username="existinguser", email="existing@example.com", password="password")
        data = {
            "username": "existinguser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "securepassword",
            "type": "customer"
        }
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_type_choice(self):
        """
        Test case to ensure that a ValidationError is raised if the 'type' field contains an invalid value.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "securepassword",
            "type": "invalid_type"
        }
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)

    def test_userprofile_is_created(self):
        """
        Test case to verify that a UserProfile is created when a user is registered.
        """
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "securepassword",
            "type": "business"
        }
        serializer = RegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        profile = serializer.save()
        self.assertEqual(UserProfile.objects.count(), 3)    # included generated guest users
        self.assertEqual(profile.type, "business")


class RegistrationViewTests(TestCase):
    """
    Test suite for the RegistrationView API to ensure proper registration functionality.
    """

    def setUp(self):
        """
        Set up the test environment, including creating valid registration data and initializing 
        the APIClient.
        """
        self.client = APIClient()
        self.register_url = "/api/registration/"  
        self.valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword",
            "repeated_password": "securepassword",
            "type": "customer"
        }

    def test_successful_registration(self):
        """
        Test case to verify that the registration API responds with success and the appropriate user and profile are created.
        """
        response = self.client.post(self.register_url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(CustomUser.objects.count(), 3)    # included generated guest users
        self.assertEqual(UserProfile.objects.count(), 3)

    def test_registration_with_invalid_data(self):
        """
        Test case to verify that the registration API returns a 400 error when invalid data is provided.
        """
        invalid_data = self.valid_data.copy()
        invalid_data["username"] = ""
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        invalid_data["email"] = ""
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_username_must_be_unique(self):
        """
        Test case to verify that the registration API returns a 400 error when the username is not unique.
        """
        CustomUser.objects.create_user(username="newuser", email="existing@example.com", password="password")
        response = self.client.post(self.register_url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_passwords_must_match(self):
        """
        Test case to ensure that the registration API returns a 400 error when passwords do not match.
        """
        mismatched_password_data = self.valid_data.copy()
        mismatched_password_data["repeated_password"] = "wrongpassword"
        response = self.client.post(self.register_url, mismatched_password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_internal_server_error_handling(self):
        """
        Test case to verify that the registration API returns a 500 error if an unexpected error occurs.
        """
        with self.assertRaises(Exception):
            response = self.client.post(self.register_url, {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("error", response.data)