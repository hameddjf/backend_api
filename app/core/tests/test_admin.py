"""
tests for the django adminn modifications.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """tests for django admin."""

    def setUp(self):
        """create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='hameddjf05@gmail.com',
            password='12345678',
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='hameddjf06@gmail.com',
            password='12345678',
            name='name user',
        )

    def test_users_list(self):
        """test that users are listed on page."""
        urls = reverse('admin:core_user_changelist')
        res = self.client.get(urls)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        """test the edit user page works."""
        urls = reverse('admin:core_user_change', args=[self.user.id])
        result = self.client.get(urls)

        self.assertEqual(result.status_code, 200)

    def test_create_user_page(self):
        """test the create user page works."""
        urls = reverse('admin:core_user_add')
        result = self.client.get(urls)

        self.assertEqual(result.status_code, 200)
