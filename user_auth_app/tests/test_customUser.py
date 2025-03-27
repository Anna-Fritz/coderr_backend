from django.test import TestCase
from ..models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission


class CustomUserModelTests(TestCase):
    """
    Test suite for testing the CustomUser model's behavior and validations.
    """

    def test_create_user_successfully(self):
        """
        Test case to verify that a user can be created successfully with valid data 
        and that the user's attributes (username, type, and password) are correctly set.
        """
        user = CustomUser.objects.create_user(username="testuser", password="testpassword", type="customer")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.type, "customer")
        self.assertTrue(user.check_password("testpassword"))

    def test_required_type(self):
        """
        Test case to verify that a ValidationError is raised when attempting to create a user 
        without providing a 'type' value (which is required).
        """
        user = CustomUser(username="testuser", password="testpassword", type=None)
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_valid_choices_of_type(self):
        """
        Test case to verify that a ValidationError is raised if an invalid 'type' value is provided 
        when creating a user.
        """
        user = CustomUser(username="testuser", password="testpassword", type="invalid_type")
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_user_can_be_assigned_to_group(self):
        """
        Test case to verify that a user can be successfully assigned to a group and 
        that the group is correctly associated with the user.
        """
        user = CustomUser.objects.create_user(username="testuser", password="testpassword", type="customer")
        group = Group.objects.create(name="TestGroup")
        user.groups.add(group)
        self.assertIn(group, user.groups.all())

    def test_user_can_have_permissions(self):
        """
        Test case to verify that a user can be assigned permissions and that the permissions 
        are correctly associated with the user.
        """
        user = CustomUser.objects.create_user(username="testuser", password="testpassword", type="customer")
        permission = Permission.objects.first()
        user.user_permissions.add(permission)
        self.assertIn(permission, user.user_permissions.all())
