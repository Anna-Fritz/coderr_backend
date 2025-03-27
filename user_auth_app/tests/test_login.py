from rest_framework.test import APITestCase
from rest_framework import status
from ..models import CustomUser


class LoginViewTests(APITestCase):
    """
    Test suite for LoginView to verify login functionality and error handling.
    """
    def setUp(self):
        """
        Sets up the initial test environment by creating a test user and defining valid login credentials.
        """
        self.login_url = "/api/login/"
        self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", password="securepassword")
        self.valid_credentials = {
            "username": "testuser",
            "password": "securepassword"
        }

    def test_successful_login(self):
        """
        Test case to verify successful login with valid credentials and the presence of a token in the response.
        """
        response = self.client.post(self.login_url, self.valid_credentials, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "testuser")

    def test_invalid_credentials(self):
        """
        Test case to verify login failure when invalid credentials are provided.
        Ensures that an appropriate error message is returned.
        """
        invalid_credentials = self.valid_credentials.copy()
        invalid_credentials["password"] = "wrongpassword"
        response = self.client.post(self.login_url, invalid_credentials, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_missing_password(self):
        """
        Test case to verify login failure when the password is missing in the request data.
        Ensures the response contains an error about the missing password field.
        """
        missing_password_data = {"username": "testuser"}
        response = self.client.post(self.login_url, missing_password_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_with_non_existing_user(self):
        """
        Test case to verify login failure when the provided username does not exist in the database.
        Ensures the response contains an error indicating the user does not exist.
        """
        non_existing_user_data = {
            "username": "nonexistent",
            "password": "securepassword"
        }
        response = self.client.post(self.login_url, non_existing_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_internal_server_error_handling(self):
        """
        Test case to verify the internal server error handling for a failed login attempt.
        Ensures the appropriate error response is returned for invalid data or unexpected errors.
        """
        with self.assertRaises(Exception):
            response = self.client.post(self.login_url, {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn("error", response.data)