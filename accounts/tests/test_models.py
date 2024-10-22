from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


class CustomUserModelTests(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            first_name = 'Test',
            last_name = 'User',
            email = 'testuser@email.com',
            password = 'testpass123'
        )

        self.admin_user = get_user_model().objects.create_superuser(
            first_name = 'Admin',
            last_name = 'User',
            email = 'adminuser@email.com',
            password = 'testpass123'
        )

        self.add_customuser = Permission.objects.get(codename='add_customuser')
        self.view_customuser = Permission.objects.get(codename='view_customuser')


    def test_create_user(self):
        """
        Test user object creation.
        """        

        self.assertEqual(self.user.email, 'testuser@email.com')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)


    def test_create_superuser(self):
        """
        Test user object superuser creation.
        """

        self.assertEqual(self.admin_user.email, 'adminuser@email.com')
        self.assertEqual(self.admin_user.first_name, 'Admin')
        self.assertEqual(self.admin_user.last_name, 'User')
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_superuser)

    
    def test_string_representation(self):
        """
        Test user model string method.
        """

        self.assertEqual(str(self.user), str(self.user.email))
        self.assertEqual(str(self.admin_user), str(self.admin_user.email))