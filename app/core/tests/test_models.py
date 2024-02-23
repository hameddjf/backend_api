"""
test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelsTests(TestCase):
    """test models."""

    def test_create_user_with_email_successful(self):
        """test creating a user with an email is successful."""
        email = 'hameddjf33@gmail.com'
        password = '12345678'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test email is normalized for new users."""
        sample_emails = [
            ['hameddjf01@GMAIL.com', 'hameddjf01@gmail.com'],
            ['HAMEDDJF02@GMAIL.COM', 'HAMEDDJF02@gmail.com'],
            ['Hameddjf03@gmail.COM', 'Hameddjf03@gmail.com'],
            ['hameddjf04@Gmail.com', 'hameddjf04@gmail.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, '12345678')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'hameddjf33@gmail.com',
            '12345678',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
